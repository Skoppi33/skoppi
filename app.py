from flask import Flask, render_template, url_for, request, redirect, make_response, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from functools import wraps  # Import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projeck2.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Важно: установите секретный ключ
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)


def is_user_registered(login):
    user = Post.query.filter_by(login=login).first()
    return user is not None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/reg')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if 'user' in session:
        return render_template("index.html", user=session['user'])
    else:
        return render_template("index.html")


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        password1 = request.form['password1']

        if password1 == password:
             if is_user_registered(login):
                 return "Пользователь с таким именем уже существует. Выберите другое имя"
             else:
                post = Post(login=login, password=password)
                try:
                    db.session.add(post)
                    db.session.commit()
                    db.session.flush()
                    session['user'] = login
                    return redirect('/')
                except IntegrityError as e:
                    print(f"Ошибка записи в базу данных: {e}")
                    return "Ошибка: пользователь с таким логином уже существует"
                except Exception as e:
                    print(f"Непредвиденная ошибка: {e}")
                    return "Непредвиденная ошибка. Попробуйте позже."
        else:
            return 'Пароли не одинаковы'
    else:
        return render_template("registr.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    login = request.form['login']
    password = request.form['password']
    user = Post.query.filter_by(login=login).first()
    if user and user.password == password:
      session['user'] = login
      return redirect("/")
    else:
       return "Неверный логин или пароль"
  else:
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/video')
@login_required  # Защищаем страницу video
def video():
    return render_template("video.html", user=session.get('user'))

@app.route('/spravochik')
@login_required  # Защищаем страницу spravochik
def spravochik():
    return render_template("spravochik.html", user=session.get('user'))

if __name__ == "__main__":
    app.run(debug=True)