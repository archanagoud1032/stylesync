from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production!

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'archu7'
app.config['MYSQL_DB'] = 'stylesync'

# Upload folder for images
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mysql = MySQL(app)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            return "Username already exists."

        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, password, role))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('index'))
        return "Invalid credentials."
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Create Look
@app.route('/create_look', methods=['GET', 'POST'])
def create_look():
    if session.get('role') != 'stylist':
        return "Access denied."

    if request.method == 'POST':
        title = request.form['title']
        tags_data = request.form['tags_data']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO looks (stylist_id, title, image) VALUES (%s, %s, %s)",
                        (session['user_id'], title, filename))
            look_id = cur.lastrowid

            tags = json.loads(tags_data)
            for tag in tags:
                cur.execute("INSERT INTO tags (look_id, x, y, tag, link) VALUES (%s, %s, %s, %s, %s)",
                            (look_id, tag['x'], tag['y'], tag['tag'], tag['link']))

            mysql.connection.commit()
            cur.close()
            return redirect(url_for('view_looks'))

    return render_template('create_look.html')

# View Looks
@app.route('/view_looks')
def view_looks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, image, stylist_id FROM looks")
    looks = cur.fetchall()

    looks_list = []
    for look_id, title, image_filename, stylist_id in looks:
        cur.execute("SELECT id, x, y, tag, link FROM tags WHERE look_id = %s", (look_id,))
        tags = cur.fetchall()
        cur.execute("SELECT username FROM users WHERE id = %s", (stylist_id,))
        stylist_name = cur.fetchone()[0]

        looks_list.append({
            'id': look_id,
            'title': title,
            'image_url': url_for('static', filename='uploads/' + image_filename),
            'tags': [{'id': t[0], 'x': t[1], 'y': t[2], 'tag': t[3], 'link': t[4]} for t in tags],
            'stylist_name': stylist_name
        })
    cur.close()
    return render_template('view_looks.html', looks=looks_list)

# Buy Product and Award Points
@app.route('/buy/<int:tag_id>')
def buy_product(tag_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT looks.stylist_id, tags.link FROM tags
        JOIN looks ON tags.look_id = looks.id
        WHERE tags.id = %s
    """, (tag_id,))
    result = cur.fetchone()

    if result:
        stylist_id, product_url = result
        cur.execute("UPDATE users SET points = points + 1 WHERE id = %s", (stylist_id,))
        mysql.connection.commit()
        cur.close()
        return redirect(product_url)
    cur.close()
    return "Tag not found."

# Stylist Dashboard
@app.route('/stylist_dashboard')
def stylist_dashboard():
    if session.get('role') != 'stylist':
        return "Access denied."

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, points FROM users WHERE id = %s", (user_id,))
    username, points = cur.fetchone()

    cur.execute("SELECT id, title, image FROM looks WHERE stylist_id = %s", (user_id,))
    looks = cur.fetchall()

    look_list = []
    for look_id, title, image in looks:
        cur.execute("SELECT id, x, y, tag, link FROM tags WHERE look_id = %s", (look_id,))
        tags = cur.fetchall()
        look_list.append({
            'id': look_id,
            'title': title,
            'image_url': url_for('static', filename='uploads/' + image),
            'tags': [{'id': t[0], 'x': t[1], 'y': t[2], 'tag': t[3], 'link': t[4]} for t in tags]
        })
    cur.close()
    return render_template('stylist_dashboard.html', username=username, points=points, looks=look_list)

# Delete Look
@app.route('/delete_look/<int:look_id>', methods=['POST'])
def delete_look(look_id):
    if session.get('role') != 'stylist':
        return "Access denied."

    cur = mysql.connection.cursor()
    cur.execute("SELECT image, stylist_id FROM looks WHERE id = %s", (look_id,))
    result = cur.fetchone()

    if not result:
        cur.close()
        return "Look not found.", 404

    image_filename, stylist_id = result

    if stylist_id != session.get('user_id'):
        cur.close()
        return "Unauthorized deletion attempt.", 403

    cur.execute("DELETE FROM looks WHERE id = %s", (look_id,))
    mysql.connection.commit()
    cur.close()

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)

    return redirect(url_for('stylist_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)