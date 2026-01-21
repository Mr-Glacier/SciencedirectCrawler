# minio_util.py

from minio import Minio
from minio.error import S3Error
from typing import Optional
import os


class MinioClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        """
        初始化 MinIO 客户端
        :param endpoint: MinIO 服务地址，如 "127.0.0.1:9000"
        :param access_key: 访问密钥
        :param secret_key: 秘密密钥
        :param secure: 是否使用 HTTPS
        """
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def make_bucket(self, bucket_name: str) -> bool:
        """
        创建存储桶
        :param bucket_name: 存储桶名称
        :return: 成功返回 True，否则 False
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created.")
            else:
                print(f"Bucket '{bucket_name}' already exists.")
            return True
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            return False

    def upload_file(self, bucket_name: str, object_name: str, file_path: str) -> bool:
        """
        上传文件到 MinIO
        :param bucket_name: 存储桶名称
        :param object_name: 上传后对象名称（可包含路径，如 "images/photo.jpg"）
        :param file_path: 本地文件路径
        :return: 成功返回 True
        """
        try:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File {file_path} not found.")

            self.client.fput_object(bucket_name, object_name, file_path)
            print(f"File '{file_path}' uploaded as '{object_name}' in bucket '{bucket_name}'.")
            return True
        except S3Error as e:
            print(f"Upload failed: {e}")
            return False

    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> bool:
        """
        下载文件
        :param bucket_name: 存储桶名称
        :param object_name: 对象名称
        :param file_path: 本地保存路径
        :return: 成功返回 True
        """
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            print(f"File '{object_name}' downloaded to '{file_path}'.")
            return True
        except S3Error as e:
            print(f"Download failed: {e}")
            return False

    def remove_file(self, bucket_name: str, object_name: str) -> bool:
        """
        删除文件
        :param bucket_name: 存储桶名称
        :param object_name: 对象名称
        :return: 成功返回 True
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            print(f"File '{object_name}' deleted from bucket '{bucket_name}'.")
            return True
        except S3Error as e:
            print(f"Delete failed: {e}")
            return False

    def list_files(self, bucket_name: str, prefix: str = "") -> list:
        """
        列出存储桶中的文件
        :param bucket_name: 存储桶名称
        :param prefix: 过滤前缀（可选）
        :return: 文件名列表
        """
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            file_list = [obj.object_name for obj in objects]
            return file_list
        except S3Error as e:
            print(f"List failed: {e}")
            return []

    def get_presigned_url(self, bucket_name: str, object_name: str, expires=3600) -> Optional[str]:
        """
        生成预签名 URL（用于临时访问）
        :param bucket_name: 存储桶名称
        :param object_name: 对象名称
        :param expires: 过期时间（秒），默认 1 小时
        :return: URL 字符串，失败返回 None
        """
        try:
            url = self.client.presigned_get_object(bucket_name, object_name, expires=expires)
            return url
        except S3Error as e:
            print(f"Generate URL failed: {e}")
            return None

    def file_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        检查文件是否存在
        :param bucket_name: 存储桶名称
        :param object_name: 对象名称
        :return: 存在返回 True
        """
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            else:
                print(f"Check existence failed: {e}")
                return False

    def upload_text(self, bucket_name: str, object_name: str, text: str):
        from io import BytesIO
        data = text.encode("utf-8")
        self.client.put_object(
            bucket_name,
            object_name,
            BytesIO(data),
            length=len(data),
            content_type="text/html"
        )

