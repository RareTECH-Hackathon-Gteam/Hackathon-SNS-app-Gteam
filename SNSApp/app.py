from flask import Flask, request, session, redirect, url_for, jsonify, flash, render_template
from flask_wtf.csrf import CSRFProtect
import os
import re
import hashlib

from models import Post

# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

csrf = CSRFProtect(app)

# signupページ表示
@app.route('/signup', methods=['GET'])
def signup_view():
    if session.get('user_id') is not None:
        return redirect(url_for('posts_view'))    ###posts_view(タイムラインの表示)を後日作成
    return render_template('auth/signup.html')    ###signup.html(サインアップ画面)を後日作成

# signup処理
@app.route('/signup', methods=['POST'])
def signup_process():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    password_confirmation = request.form.get('password_confirmation', '')
    # 空欄チェック
    if not name or not email or not password or not password_confirmation:
        flash('全ての項目を入力してください', 'error')
        return redirect(url_for('signup_view'))
    # passwordとpassword_confirmationの一致チェック
    if password != password_confirmation:
        flash('パスワードが一致しません', 'error')
        return redirect(url_for('signup_view'))
    # emailの形式チェック
    if re.match(EMAIL_PATTERN, email) is None:
        flash('メールアドレスの形式が正しくありません', 'error')
        return redirect(url_for('signup_view'))
    # 既存userの存在チェック
    registered_user = User.fined_by_email(email)    ###後日Userクラスを作成
    if registered_user is not None:
        flash('既に登録されているメールアドレスです', 'error')
        return redirect(url_for('signup_view'))
    # passwordのハッシュ化
    hushed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # ユーザー登録処理
    user_id = User.create(name, email, hushed_password)    ###後日Userクラスを作成
    session['user_id'] = user_id
    flash('登録完了！', 'success')
    return redirect(url_for('posts_view'))    ###posts_view(タイムラインの表示

# 投稿処理
@app.route('/posts', methods=['POST'])
def create_post():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))    ###login_view(ログイン画面の表示)を後日作成
    contents = request.form.get('content', '').strip()
    if contents == '':
        flash ('投稿内容が空です', 'error')
        return redirect(url_for('posts_view'))    ###posts_view(タイムラインの表示)を後日作成
    Post.create(user_id, contents)
    flash('投稿完了！', 'success')
    return redirect(url_for('posts_view'))    ###posts_view(タイムラインの表示)を後日作成


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)    ###debug=Trueは後で変更？