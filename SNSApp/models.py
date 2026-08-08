from flask import abort
import pymysql
from util.DB import DB    ###後日DB.pyファイルを作成

db_pool = DB.init_db_pool()    ###後日DB.pyファイルを作成

# Postsクラス
class Post:
    @classmethod
    def create(cls, user_id, contents):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO posts (user_id, contents) VALUES (%s, %s);"
                cur.execute(sql, (user_id, contents))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

