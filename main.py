import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'Clw_23'

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id  # Aquí self.id es el id_usuario
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def get_db_connection():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_comments_for_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    #contenido del comentario y el nombre de usuario del autor
    cursor.execute('''
        SELECT c.content, u.username FROM Comentario c
        JOIN Usuario u ON c.user_id = u.id_usuario
        WHERE c.post_id = ? ORDER BY c.id ASC
    ''', (post_id,))
    comments = cursor.fetchall()
    conn.close()
    return [{'content': c['content'], 'username': c['username']} for c in comments]


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM Usuario WHERE id_usuario = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/blog')
def blog():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
            SELECT post.id, post.title, post.content, post.id_usuario,
            Usuario.username, COUNT(like.id) AS likes FROM POST
            LEFT JOIN Usuario ON post.id_usuario = Usuario.id_usuario
            LEFT JOIN like ON post.id = like.post_id
            GROUP BY post.id, post.title, post.content, 
            post.id_usuario, Usuario.username
            ORDER BY post.id DESC''')  #Uso ORDER DESC para mostrar los más nuevos primero
    result = cursor.fetchall()

    posts = []
    for post in result:
        post_data = dict(post)
        post_data['comments'] = get_comments_for_post(post_data['id'])
        if current_user.is_authenticated:
            #post.id para ver si el post ha sido likeado por el user_id
            is_liked = conn.execute(
                'SELECT 1 FROM like WHERE user_id = ? AND post_id = ?',(current_user.id, post_data['id'])).fetchone()
            post_data['is_liked'] = bool(is_liked)
        else:
            post_data['is_liked'] = False
        posts.append(post_data)
    conn.close()
    context = {'posts': posts}
    return render_template('blog.html', **context)


@app.route('/moovies')
def moovies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM peliculas')
    result = cursor.fetchall()
    items = []
    for peliculas in result:
        items.append({
            'id': peliculas[0], 'title': peliculas[1], 'contenido': peliculas[2]})
    conn.close()
    mov = {'items': items}
    return render_template('peliculas.html', **mov)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if not title or not content:
            flash('Título y contenido son obligatorios.')
            return redirect(url_for('add'))

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO POST (title, content, id_usuario) VALUES (?, ?, ?)',
            (title, content, current_user.id)  # current_user.id es el id_usuario
        )
        conn.commit()
        conn.close()
        flash('Publicación creada con éxito.')
        return redirect(url_for('blog'))
    return render_template('post_nuevo.html')

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT title, content, id_usuario FROM POST WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        conn.close()
        flash('Post no encontrado.')
        return redirect(url_for('blog'))
    # post[2] contiene el id_usuario del autor
    if post['id_usuario'] != current_user.id:
        conn.close()
        flash('No tienes permiso para editar este post.')
        return redirect(url_for('blog'))

    if request.method == 'POST':
        #procesar la actualización
        new_title = request.form.get('title')
        new_content = request.form.get('content')
        conn.execute(
            'UPDATE POST SET title = ?, content = ? WHERE id = ?',
            (new_title, new_content, post_id)
        )
        conn.commit()
        conn.close()
        flash('Post actualizado con éxito.')
        return redirect(url_for('blog'))

    #mostrar el formulario (GET)
    conn.close()
    context = {'title': post['title'], 'content': post['content'], 'post_id': post_id}
    return render_template('edit_post.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM Usuario WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and User(user[0], user[1], user[2]).check_password(password):
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('blog'))
        else:
            return render_template('login.html', message='Usuario o contraseña inválidos.')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        correo = request.form['correo']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO Usuario (username, correo, password_hash) VALUES (?, ?, ?)",
                         (username, correo, generate_password_hash(password, method='pbkdf2:sha256')))
            conn.commit()
            print('Registro exitoso')
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', advertencia='El usuario ya existe, intente otra combinación.')
    return render_template('register.html')


@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM POST WHERE id = ?", (post_id,)).fetchone()

    # post[3] es el id_usuario
    if post and post['id_usuario'] == current_user.id:
        # Elimino likes, comentarios y el post para evitar errores de clave foránea
        conn.execute("DELETE FROM like WHERE post_id = ?", (post_id,))
        conn.execute("DELETE FROM Comentario WHERE post_id = ?", (post_id,))
        conn.execute("DELETE FROM POST WHERE id = ?", (post_id,))
        conn.commit()
        flash('Post eliminado con éxito.')
    conn.close()
    return redirect(url_for('blog'))

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    comment_content = request.form.get('comment_content')

    if not comment_content:
        flash('El comentario no puede estar vacío.')
        return redirect(url_for('blog'))
    user_id = current_user.id
    conn = get_db_connection()
    conn.execute('INSERT INTO Comentario (post_id, user_id, content) VALUES (?, ?, ?)',
                 (post_id, user_id, comment_content))
    conn.commit()
    conn.close()
    flash('Comentario agregado.')
    return redirect(url_for('blog'))

def user_is_liking(user_id, post_id):
    conn = get_db_connection()
    like = conn.execute('SELECT * FROM like WHERE user_id = ? AND post_id = ?', (user_id, post_id)).fetchone()
    conn.close()
    return bool(like)

@app.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM POST WHERE id = ?', (post_id,)).fetchone()
    if post:
        if user_is_liking(current_user.id, post_id):
            conn.execute('DELETE FROM like WHERE user_id = ? AND post_id = ?', (current_user.id, post_id))
            print('You unliked this post')
        else:
            conn.execute('INSERT INTO like (user_id, post_id) VALUES (?, ?)', (current_user.id, post_id))
            print('You liked this post')
        conn.commit()
        conn.close()
        return redirect(url_for('blog'))
    conn.close()
    return 'Post not found', 404

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False)