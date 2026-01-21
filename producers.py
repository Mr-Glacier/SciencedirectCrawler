import time
import uuid
from rabbitmq_util import RabbitMQUtil

# ===== MQ 配置 (需与消费者一致) =====
mq = RabbitMQUtil(
    host="192.168.0.210",
    port=32288,
    user="admin",
    password="admin123",
    vhost="/"
)

# 示例：待爬取的 ScienceDirect 文章 URL 列表
# 你可以替换为从文件、数据库读取的逻辑
URL_LIST = [
    "https://www.sciencedirect.com/journal/13590286/years?page-size=20&page=1",
    "https://www.sciencedirect.com/journal/13590286/years?page-size=20&page=2"
]


def send_crawl_tasks():
    print(f"📊 准备发送 {len(URL_LIST)} 个爬取任务...")

    for idx, url in enumerate(URL_LIST, 1):
        # 1. 构建任务消息
        task_message = {
            "taskId": str(uuid.uuid4()),  # 生成唯一任务ID
            "url": url.strip(),  # 确保 URL 没有多余空格
            "priority": 1,  # 可选：任务优先级
            "timestamp": time.time()  # 任务生成时间戳
        }

        # 2. 发送消息到队列
        try:
            mq.send("q.crawl.task", task_message)
            print(f"✅ [{idx}/{len(URL_LIST)}] 已发送: {url}")

        except Exception as e:
            print(f"❌ [{idx}] 发送失败 {url}: {str(e)}")

    print("🚀 所有任务已发送完毕！")


if __name__ == '__main__':
    send_crawl_tasks()