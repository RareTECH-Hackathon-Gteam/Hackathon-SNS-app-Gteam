from flask import Flask, request, session, redirect, url_for, jsonify, flash, render_template, abort
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import os
import re
import hashlib

from models import User, Post, Reaction

# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# リアクション名とIDを辞書オブジェクト（定数）として定義する
REACTION_NAME_DIC = {
    "good": 1,
    "study": 2
}

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
app.permanent_session_lifetime = timedelta(days=30)

@app.before_request
def make_session_permanent():
    session.permanent = True

csrf = CSRFProtect(app)

# signupページ表示
@app.route('/signup', methods=['GET'])
def signup_view():
    if session.get('user_id') is not None:
        return redirect(url_for('posts_view'))
    return render_template('auth/signup.html')

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
    registered_user = User.find_by_email(email)
    if registered_user is not None:
        flash('既に登録されているメールアドレスです', 'error')
        return redirect(url_for('signup_view'))
    # passwordのハッシュ化
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # ユーザー登録処理
    user_id = User.create(name, email, hashed_password)
    session['user_id'] = user_id
    flash('登録完了！', 'success')
    return redirect(url_for('posts_view'))

# loginページ表示
@app.route('/login', methods=['GET'])
def login_view():
    if session.get('user_id') is not None:
        return redirect(url_for('posts_view'))
    return render_template('auth/login.html')

# login処理
@app.route('/login', methods=['POST'])
def login_process():
    email = request.form.get('email')
    password = request.form.get('password')
    # 空欄チェック
    if not email or not password:
        flash('全ての項目を入力してください', 'error')
    else:
        user = User.find_by_email(email)
        if user is None:
            flash('メールアドレスまたはパスワードが間違っています', 'error')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user['password']:
                flash('メールアドレスまたはパスワードが間違っています', 'error')
            else:
                session['user_id'] = user['id']
                flash('ログイン完了！', 'success')
                return redirect(url_for('posts_view'))
    return redirect(url_for('login_view'))

# logout処理
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('ログアウトしました', 'success')
    return redirect(url_for('posts_view'))

# タイムラインの表示
@app.route('/', methods=['GET'])
def posts_view():
    user_id = session.get('user_id')
    posts = Post.get_all()
    for post in posts:
        post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
    return render_template('post/post.html', posts=posts, user_id=user_id, header_type = 'timeline')

# 投稿画面の表示
@app.route('/posts', methods=['GET'])
def create_post_page():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    return render_template('post/create_post.html', header_type = 'cancel')

# 投稿処理
@app.route('/posts', methods=['POST'])
def create_post():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    contents = request.form.get('content', '').strip()
    if contents == '':
        flash('投稿内容が空です', 'error')
        return redirect(url_for('create_post_page'))
    if len(contents) > 140:
        flash('140文字以内で入力してください', 'error')
        return redirect(url_for('create_post_page'))
    Post.create(user_id, contents)
    flash('投稿完了！', 'success')
    return redirect(url_for('posts_view'))

# 投稿削除機能
@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    post = Post.find_by_id(post_id)
    if post is None:
        abort(404)
    if post['user_id'] != user_id:
        flash('この投稿を削除することはできません', 'error')
        return redirect(url_for('posts_view')) 

    Post.delete(post_id)
    flash('投稿が削除されました', 'success')
    return redirect(url_for('my_page_view', user_id=user_id))

# リアクションの処理（URLのリアクション名の部分も変数として受け取る）
@app.route('/posts/<int:post_id>/<string:reaction_name>', methods=['POST'])
def react_to_post(post_id, reaction_name):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    # 登録した辞書からIDを取得
    reaction_id = REACTION_NAME_DIC.get(reaction_name)
    # リアクションのトグル処理を実行
    Reaction.toggle_reaction(user_id, post_id, reaction_id)
    # posts_viewへリダイレクトする
    return redirect(url_for('posts_view'))

# マイページ表示
@app.route('/my_page/<int:user_id>', methods=['GET'])
def my_page_view(user_id):
    user_name = User.get_name_by_id(user_id)
    if user_name is None:
        return redirect(url_for('login_view'))
    # ユーザーの投稿を取得
    posts = Post.get_own_posts(user_id)
    for post in posts:
        post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
    return render_template('users/my_page.html', user_name=user_name, posts=posts, header_type = 'mypage')

@app.errorhandler(400)
def bad_request(error):
    return render_template('error/400.html'), 400

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error/500.html'), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)    ###debug=Trueは後で変更？