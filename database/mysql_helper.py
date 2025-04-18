import sqlite3

# 连接到数据库（如果不存在则创建）
conn = sqlite3.connect('saga_main.db')
# 创建游标
cursor = conn.cursor()


def create_default_tables():
    # # 创建表
    # cursor.execute('''CREATE TABLE IF NOT EXISTS `users`
    #                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                   username VARCHAR(255) NOT NULL,
    #                   password  VARCHAR(64) NOT NULL,
    #                   nick_name VARCHAR(255),
    #                   email VARCHAR(255) unique,
    #                   activated INT default 0,
    #                   create_time datetime default (datetime('now', 'localtime')),
    #                   uid VARCHAR(64) NOT NULL unique,
    #                   session_id VARCHAR(255),
    #                   session_time TIMESTAMP,
    #                   activate_code INT default 0,
    #                   activate_prepare_time TIMESTAMP,
    #                   pay_id VARCHAR(128) NOT NULL)''')
    return


def write_db(sql: str):
    cursor.execute(sql)
    return conn.commit()


def params_update_db(sql, data):
    cursor.execute(sql, data)
    affected_rows = cursor.rowcount
    return conn.commit(), affected_rows


def update_db(sql: str):
    """
    :param sql:
    :return: 异常str(无异常返回None), 影响的行数
    """
    cursor.execute(sql)
    affected_rows = cursor.rowcount
    return conn.commit(), affected_rows


def write_db_para(sql: str, params):
    cursor.execute(sql, params)
    affected_rows = cursor.rowcount
    return conn.commit(), affected_rows


def read_db(sql: str):
    cursor.execute(sql)
    return cursor.fetchall()


def close():
    conn.close()
