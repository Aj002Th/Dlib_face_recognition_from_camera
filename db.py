import sqlite3
import logging

# db操作
class DB:
    def __init__(self, file):
        # 连接数据库
        self.conn = sqlite3.connect(file)
        logging.info("Opened database successfully")

        # 创建 user 表
        self.conn.execute('''
        CREATE TABLE  IF NOT EXISTS user(
            id INTEGER primary key AUTOINCREMENT,
            username text,
            password text
        )
        ''')

    def insert(self, username, password):
        self.conn.execute(f'''
        INSERT INTO user (username, password) VALUES ('{username}', '{password}')
        ''')
        self.conn.commit()
        logging.info("Records created successfully")
    
    def select(self, username, password):
        cursor = self.conn.execute(f'''
        SELECT * FROM user WHERE username = '{username}' AND password = '{password}'
        ''')
        return cursor.fetchall()
    
    def selectByUsername(self, username):
        cursor = self.conn.execute(f'''
        SELECT * FROM user WHERE username = '{username}'
        ''')
        return cursor.fetchall()