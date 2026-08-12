import os
import pymysql
from pymysqlpool.pool import Pool


class DB:
    @classmethod
    def init_db_pool(cls):
        pool = Pool(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            db=os.environ['DB_DATABASE'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            max_size=5
        )
        pool.init()
        return pool