### 📚 ScienceDirect 爬虫系统文档

本项目是一个基于 **Playwright** 的高可用 ScienceDirect 爬虫系统，支持持久化登录状态、自动绕过 Cloudflare 验证，并通过消息队列与对象存储实现解耦，具备良好的可扩展性与容错能力。

---

#### ✨ 核心特性

- **浏览器常驻 + Cookie 持久化**  
  使用 Playwright 启动常驻浏览器，通过 `storage_state` 保存登录状态，避免重复人机验证。
  
- **Cloudflare 防护应对机制**  
  自动检测 “Are you a robot” 页面，触发 **语音播报 + 系统提示音** 告警，提示人工介入完成验证。

- **告警通知机制**  
  集成系统级声音提醒，确保及时响应验证码拦截。

- **分布式架构设计**  
  爬虫任务与 **RabbitMQ**（消息队列）和 **MinIO/S3**（对象存储）解耦，支持横向扩展，适合大规模部署。

---

#### ⚙️ 配置说明

```python
# ===== 消息队列 (RabbitMQ) =====
mq = RabbitMQUtil(
    host="192.168.0.210",
    port=32288,
    user="admin",
    password="admin123",
    vhost="/"
)

# ===== 对象存储 (MinIO) =====
minio = MinioClient(
    endpoint="192.168.0.210:9110",
    access_key="Zumo0ma0IBn0sU0DTUDn",
    secret_key="T8pPv9pCWist4lUdXgOjE4llwTmHEZqjCOxNiH01",
    secure=False
)

# ===== Playwright 配置 =====
STORAGE_STATE_FILE = "D:\\programWorkPlace\\SciencedirectCrawler\\storage_state.json"
BUCKET = "crawl-science-direct"
```
#### ✨ 核心特性
- STORAGE_STATE_FILE：Playwright 持久化 Cookie 的本地路径，请根据实际环境修改。
- 首次运行需手动验证：首次访问 网站时可能触发 Cloudflare 人机验证，请在浏览器中手动完成验证，之后状态将被保存至 storage_state.json，后续运行将自动复用会话，尽可能绕过验证。
---
#### 📂 项目目录结构
```textmate
crawler/
├── main.py               # 爬虫主程序入口（crawler_worker）
├── producers.py          # 任务生产者：将待爬取 URL 推送至 RabbitMQ
├── minio_util.py         # MinIO 客户端封装工具
├── rabbitmq_util.py      # RabbitMQ 工具封装
├── storage_state.json    # Playwright 浏览器状态与 Cookie 持久化文件
├── README.md             # 项目说明文档
```