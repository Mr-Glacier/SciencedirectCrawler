# sqlite_util.py
import sqlite3
import logging
from typing import List, Tuple, Any, Optional


class SQLiteManager:
    def __init__(self, db_path: str):
        """
        初始化数据库管理器
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON;")
            self.connection.commit()
            logging.info(f"成功连接到数据库: {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"连接数据库失败: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logging.info("数据库连接已关闭")

    def execute_query(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Cursor]:
        """
        执行查询语句 (SELECT)
        :param query: SQL 查询语句
        :param params: 参数元组
        :return: 游标对象
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            logging.error(f"查询执行失败: {e}")
            return None

    def execute_non_query(self, query: str, params: Tuple = ()) -> bool:
        """
        执行非查询语句 (INSERT, UPDATE, DELETE, CREATE)
        :param query: SQL 语句
        :param params: 参数元组
        :return: 成功返回 True
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"非查询语句执行失败: {e}")
            self.connection.rollback()
            return False

    def create_table(self, create_table_sql: str) -> bool:
        """
        创建数据表
        :param create_table_sql: CREATE TABLE 语句
        :return: 成功返回 True
        """
        return self.execute_non_query(create_table_sql)

    def insert_record(self, table: str, columns: List[str], values: Tuple) -> bool:
        """
        插入一条记录
        :param table: 表名
        :param columns: 列名列表
        :param values: 值元组
        :return: 成功返回 True
        """
        placeholders = ', '.join('?' * len(values))
        columns_str = ', '.join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        return self.execute_non_query(query, values)

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        获取所有查询结果
        :param query: SQL 查询语句
        :param params: 参数元组
        :return: 结果列表
        """
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """
        获取一条查询结果
        :param query: SQL 查询语句
        :param params: 参数元组
        :return: 单条结果或 None
        """
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def update_record(self, table: str, set_clause: str, where_clause: str, params: Tuple) -> bool:
        """
        更新记录
        :param table: 表名
        :param set_clause: SET 子句 (例如 "name=?, age=?")
        :param where_clause: WHERE 子句 (例如 "id=?")
        :param params: 参数元组
        :return: 成功返回 True
        """
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        return self.execute_non_query(query, params)

    def delete_record(self, table: str, where_clause: str, params: Tuple) -> bool:
        """
        删除记录
        :param table: 表名
        :param where_clause: WHERE 子句
        :param params: 参数元组
        :return: 成功返回 True
        """
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_non_query(query, params)

    def __enter__(self):
        """支持上下文管理器 (with 语句)"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动关闭连接"""
        self.close()
