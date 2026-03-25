from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_login import (LoginManager, UserMixin, login_user,
                         logout_user, login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

app = Flask(__name__, template_folder='templates')

app.config['SECRET_KEY'] = 'Z_Pmfi892.**'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

DATABASE = 'base_datos.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    # Configura para que las filas se puedan acceder como diccionarios (por nombre de columna)
    conn.row_factory = sqlite3.Row
    return conn

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    conn = get_db() # La conexión se abre solo para el user_loader
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM user_data WHERE id_usuario = ?', (user_id,)).fetchone()
    conn.close()

    if user is not None:
        return User(user['id_usuario'], user['username'], user['password'])
    return None

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            mensaje_problema = "Faltan el usuario o la contraseña."
            return render_template('login.html')

        conn = get_db() #Abro
        cursor = conn.cursor()

        user = cursor.execute('SELECT * FROM user_data WHERE username = ?',
                              (username,)).fetchone()
        conn.close() #Cierro


    return render_template('login.html')


@app.route('/blog')
#@login_required  # Protege el blog
def blog():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM POST JOIN user_data ON POST.id_usuario = user_data.id_usuario')
    result = cursor.fetchall()
    print(result)
    posts = []

    for post in (result):
        posts.append({'id': post[0], 'title': post[1], 'content': post[2], 'id_usuario': post[3], 'username': post[4], 'correo': post[5]})

    conn.close()
    context = {'posts': posts}
    print(context)
    return render_template('blog.html', **context, user=current_user.username)

if __name__ == '__main__':
    app.run(debug=False)