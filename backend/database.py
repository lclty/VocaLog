import sqlite3
import json

DB_PATH = 'vocalog.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 允许通过列名访问
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # 新表结构：增加了 path (路径), staff (JSON), progress (JSON)
        c.execute('''CREATE TABLE IF NOT EXISTS projects
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      singer TEXT NOT NULL,
                      status TEXT, 
                      path TEXT,
                      staff TEXT,
                      progress TEXT)''')
        conn.commit()