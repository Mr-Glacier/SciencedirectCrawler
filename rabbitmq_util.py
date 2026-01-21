import json
import time
import pika
from typing import Callable, Any


class RabbitMQUtil:
    """
    一个类同时搞定：
    - 生产者
    - 消费者
    - 自动建队列
    - 自动重连
    """

    def __init__(
            self,
            host="localhost",
            port=5672,
            user="guest",
            password="guest",
            vhost="/",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost

        self._connection = None
        self._channel = None

    # ================= 连接管理 =================

    def _get_channel(self):
        """获取 channel，带自动重连"""
        if self._channel and self._channel.is_open:
            return self._channel

        while True:
            try:
                credentials = pika.PlainCredentials(
                    self.user, self.password
                )

                params = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.vhost,
                    credentials=credentials,
                    heartbeat=60,
                )

                self._connection = pika.BlockingConnection(params)
                self._channel = self._connection.channel()

                return self._channel

            except Exception as e:
                print("[RabbitMQ] 连接失败，重试:", e)
                time.sleep(3)

    # ================= 生产者 =================

    def send(self, queue: str, message: Any):
        """
        发送消息

        RabbitMQUtil().send("q.test", {"a": 1})
        """
        ch = self._get_channel()

        # 自动建队列
        ch.queue_declare(queue=queue, durable=True)

        body = (
            json.dumps(message, ensure_ascii=False)
            if not isinstance(message, str)
            else message
        )

        ch.basic_publish(
            exchange="",
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # 持久化
            ),
        )

    # ================= 消费者 =================

    def consume(
            self,
            queue: str,
            handler: Callable[[dict], bool],
            prefetch: int = 1,
    ):
        """
        消费消息

        handler 返回：
            True  -> ack
            False -> nack 重回队列
        """

        ch = self._get_channel()

        ch.queue_declare(queue=queue, durable=True)
        ch.basic_qos(prefetch_count=prefetch)

        def callback(channel, method, props, body):

            try:
                data = json.loads(body)
            except:
                data = body

            try:
                result = handler(data)

                if result:
                    channel.basic_ack(method.delivery_tag)
                else:
                    channel.basic_nack(
                        method.delivery_tag,
                        requeue=True,
                    )

            except Exception as e:
                print("[RabbitMQ] 业务异常:", e)

                channel.basic_nack(
                    method.delivery_tag,
                    requeue=True,
                )

        ch.basic_consume(
            queue=queue,
            on_message_callback=callback,
        )

        print(f"[RabbitMQ] 开始消费队列: {queue}")
        ch.start_consuming()
