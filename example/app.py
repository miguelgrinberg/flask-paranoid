from flask import Flask, render_template, request, redirect
from flask_paranoid import Paranoid
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
login_manager = LoginManager(app)
paranoid = Paranoid(app)
paranoid.redirect_view = '/'


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(id):
    return User(id)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('username'):
            remember = request.form.get('remember_me') is not None
            login_user(User(request.form.get('username')), remember=remember)
        else:
            logout_user()
        return redirect('/')
    else:
        return render_template(
            'index.html', username=current_user.id 
            if current_user.is_authenticated else None)