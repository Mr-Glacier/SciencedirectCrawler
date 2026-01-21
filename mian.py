import os
import random
import time
import uuid

import pyttsx3
from playwright.sync_api import sync_playwright

from minio_util import MinioClient
from rabbitmq_util import RabbitMQUtil
import winsound

# ===== MQ =====
mq = RabbitMQUtil(
    host="192.168.0.210",
    port=32288,
    user="admin",
    password="admin123",
    vhost="/"
)

# ===== MinIO =====
minio = MinioClient(
    endpoint="192.168.0.210:9110",
    access_key="123123213",
    secret_key="123124134",
    secure=False
)
STORAGE_STATE_FILE = "D:\\programWorkPlace\\SciencedirectCrawler\\storage_state.json"
BUCKET = "crawl-science-direct"


def handle_task(context, msg):
    page = context.new_page()

    try:
        url = msg.get("url")
        if not url:
            return True

        time.sleep(random.uniform(0.5, 1.5))

        page.goto(url, timeout=20000)
        page.wait_for_load_state("domcontentloaded")
        # 如果出现了人机验证,则手动处理
        error_card = page.locator(".error-card")
        if error_card.is_visible():
            winsound.MessageBeep(winsound.MB_ICONHAND)
            wait_error_card_with_tts(page)
            error_card.wait_for(state="detached", timeout=1000 * 1000)
        time.sleep(random.uniform(0.5, 1.5))
        page.wait_for_load_state("domcontentloaded")
        html = page.content()
        # ====== 存 MinIO ======
        task_id = msg.get("taskId") or str(uuid.uuid4())

        object_name = (
            f"crawl/{time.strftime('%Y/%m/%d')}/"
            f"{task_id}.html"
        )

        minio.upload_text(
            bucket_name=BUCKET,
            object_name=object_name,
            text=html
        )

        # ====== MQ 只传路径 ======
        mq.send("q.crawl.html", {
            "taskId": task_id,
            "url": url,
            "htmlPath": object_name,
            "bucket": BUCKET,
            "crawlTime": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        save_context(context)
        print(f"✅ [{task_id}] 已保存: {object_name}")
        return True

    except Exception as e:
        mq.send("q.crawl.failed", {
            "task": msg,
            "error": str(e),
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        return False

    finally:
        try:
            page.close()
        except:
            pass


# =============== Worker 主进程 ===============

def crawler_worker():
    # 确保 bucket 存在（一次即可）
    minio.make_bucket(BUCKET)

    with sync_playwright() as p:
        print("🚀 启动常驻 Chrome...")

        # ✅ 常驻 Browser
        browser = p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox",
            ],
        )

        context = create_context(browser)

        def mq_handler(msg):
            return handle_task(context, msg)

        mq.consume("q.crawl.task", mq_handler)




def create_context(browser):
    if os.path.exists(STORAGE_STATE_FILE):
        print("🍪 加载已有 Cookie")
        return browser.new_context(
            storage_state=STORAGE_STATE_FILE,
            viewport=None
        )
    else:
        print("🍪 无 Cookie，新建 Context")
        return browser.new_context(viewport=None)


def save_context(context):
    """将当前上下文的状态保存到本地文件"""
    print(f"💾 正在保存状态到 {STORAGE_STATE_FILE}")
    context.storage_state(path=STORAGE_STATE_FILE)


engine = pyttsx3.init()
engine.setProperty("rate", 160)  # 语速
engine.setProperty("volume", 1.0)


def speak(text):
    engine.say(text)
    engine.runAndWait()


def wait_error_card_with_tts(page):
    error_card = page.locator(".error-card")
    last_speak = 0

    while error_card.is_visible():
        now = time.time()
        if now - last_speak >= 30:
            speak("检测到验证码，请尽快处理")
            last_speak = now
        time.sleep(1)

    speak("验证码已通过，任务恢复")


if __name__ == '__main__':
    crawler_worker()
