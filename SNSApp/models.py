from flask import abort
import pymysql
from util.DB import DB

db_pool = DB.init_db_pool()

# Userクラス
class User:
    @classmethod
    def create(cls, name, email, password):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s);"
                cur.execute(sql, (name, email, password))
                conn.commit()
                # AUTO_INCREMENTで生成されたidを返す
                return cur.lastrowid
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_email(cls, email):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM users WHERE email = %s;"
                cur.execute(sql, (email,))
                user = cur.fetchone()
            return user
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_name_by_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT name FROM users WHERE id = %s;"
                cur.execute(sql, (user_id,))
                user = cur.fetchone()
            return user['name'] if user else None
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Postsクラス
class Post:
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                        SELECT \
                            p.id, \
                            p.user_id, \
                            p.contents, \
                            p.created_at, \
                            u.name AS user_name, \
                        COUNT(CASE WHEN r.reaction_id = 1 THEN 1 END) AS good_count, \
                        COUNT(CASE WHEN r.reaction_id = 2 THEN 1 END) AS study_count \
                        From posts p \
                            INNER JOIN users u ON p.user_id = u.id AND u.deleted_at IS NULL\
                            LEFT JOIN reactions r ON p.id = r.post_id \
                        WHERE p.deleted_at IS NULL \
                        GROUP BY p.id, p.contents, p.created_at, u.name \
                        ORDER BY p.created_at DESC;
                        """
                cur.execute(sql)
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

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

    # マイページの投稿取得
    @classmethod
    def get_own_posts(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                        SELECT \
                            p.id, \
                            p.contents, \
                            p.created_at, \
                            u.name AS user_name, \
                            COUNT(CASE WHEN r.reaction_id = 1 THEN 1 END) AS good_count, \
                            COUNT(CASE WHEN r.reaction_id = 2 THEN 1 END) AS study_count \
                        FROM posts p \
                        INNER JOIN users u ON p.user_id = u.id AND u.id = %s AND u.deleted_at IS NULL \
                        LEFT JOIN reactions r ON p.id = r.post_id \
                        WHERE p.deleted_at IS NULL \
                        GROUP BY p.id, p.contents, p.created_at, u.name \
                        ORDER BY p.created_at DESC;
                        """
                cur.execute(sql, (user_id,))
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE posts SET deleted_at = NOW() WHERE id = %s:"
                cur.execute(sql, (post_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM posts WHERE id = %s AND deleted_at IS NULL;"
                cur.execute(sql, (post_id,)) 
                post = cur.fetchone()
            return post
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

#Reactionクラス
class Reaction:
    @classmethod
    # リアクションのトグル処理
    def toggle_reaction(cls, user_id, post_id, reaction_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                # リアクションがすでに存在するかをチェック
                check_sql = "SELECT id FROM reactions WHERE user_id = %s AND post_id = %s AND reaction_id = %s;"
                cur.execute(check_sql, (user_id, post_id, reaction_id))
                existing_reaction = cur.fetchone()
                # 分岐処理
                # リアクションが存在しなかった場合は追加する
                if existing_reaction is None:
                    insert_sql = "INSERT INTO reactions (user_id, post_id, reaction_id) VALUES (%s, %s, %s);"
                    cur.execute(insert_sql, (user_id, post_id, reaction_id))
                # リアクションがすでに存在していた場合は削除する
                else:
                    delete_sql = "DELETE FROM reactions WHERE user_id = %s AND post_id = %s AND reaction_id = %s;"
                    cur.execute(delete_sql, (user_id, post_id, reaction_id))
                conn.commit()   ###コミットして確定させる
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
        
    # リアクション数カウント
    @classmethod
    def count_reaction(cls, post_id, reaction_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT COUNT(*) FROM reactions WHERE post_id = %s AND reaction_id = %s;"
                cur.execute(sql, (post_id, reaction_id))
                result = cur.fetchone()
                # カウント結果がタプルで返ってくるので、その要素を取り出して変数に格納
                reaction_count = result[0]  
            return reaction_count
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)