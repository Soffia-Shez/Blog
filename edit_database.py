import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
connection = sqlite3.connect('base_datos.db', check_same_thread=False)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

password_cuenta = []

cursor.execute('INSERT INTO user_data VALUES (?,?,?)',
    (1, 'Ssanchez', generate_password_hash('0123')))

cursor.execute('UPDATE post SET id_usuario = 1;')

print(password_cuenta)
connection.commit()
connection.close()