from flask import Flask, request, session, redirect, url_for, jsonify, flash
from flask_wtf.csrf import CSRFProtect
import os

from models import Post

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

csrf = CSRFProtect(app)


# 投稿処理
@app.route('/posts', methods=['POST'])
def create_post():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))    ###login_view(ログインページの表示)を後日作成
    content = request.form.get('content', '').strip()
    if content == '':
        flash ('投稿内容が空です', 'error')
        return redirect(url_for('posts_view'))    ###posts_view(タイムラインの表示)を後日作成
    Post.create(user_id, contents)
    flash('投稿完了！', 'success')
    return redirect(url_for('posts_view'))    ###posts_view(タイムラインの表示)を後日作成


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)    ###debug=Trueは後で変更？