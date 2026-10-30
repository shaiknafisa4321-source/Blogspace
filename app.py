import os
from functools import wraps
import mysql.connector
from flask import Flask, render_template, request
from flask import redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
app = Flask(__name__)
app.secret_key = "blogspace_secret_key"
# Database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_PASSWORD"),
        database="blogspace"
    )
# Login required decorator
def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first!")
            return redirect(url_for("login"))
        return route(*args, **kwargs)
    return wrapper
# Home page
@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT posts.*, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """)
    posts = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("index.html", posts=posts)
# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            db.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Email already registered!")
        finally:
            cursor.close()
            db.close()
    return render_template("register.html")
# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        flash("Invalid email or password!")
    return render_template("login.html")
# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
# Create blog post
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
            (session["user_id"], title, content)
        )
        db.commit()
        cursor.close()
        db.close()
        flash("Blog published successfully!")
        return redirect(url_for("index"))
    return render_template("create.html")
# View single post and comments
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        if "user_id" not in session:
            flash("Please login to comment!")
            return redirect(url_for("login"))
        comment = request.form["comment"]
        if comment.strip():
            cursor.execute(
                "INSERT INTO comments (post_id, user_id, comment) VALUES (%s, %s, %s)",
                (post_id, session["user_id"], comment)
            )
            db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("post", post_id=post_id))
    cursor.execute("""
        SELECT posts.*, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.id = %s
    """, (post_id,))
    blog = cursor.fetchone()
    if not blog:
        cursor.close()
        db.close()
        return "Post not found", 404
    cursor.execute("""
        SELECT comments.*, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = %s
        ORDER BY comments.id DESC
    """, (post_id,))
    comments = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template(
        "post.html",
        blog=blog,
        comments=comments
    )
# Edit blog
@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit(post_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM posts WHERE id = %s AND user_id = %s",
        (post_id, session["user_id"])
    )
    blog = cursor.fetchone()
    if not blog:
        cursor.close()
        db.close()
        return "Post not found or unauthorized", 404
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        cursor.execute(
            "UPDATE posts SET title = %s, content = %s WHERE id = %s AND user_id = %s",
            (title, content, post_id, session["user_id"])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("post", post_id=post_id))
    cursor.close()
    db.close()
    return render_template("edit.html", blog=blog)
# Delete blog
@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM posts WHERE id = %s AND user_id = %s",
        (post_id, session["user_id"])
    )
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for("index"))
# REST API - Get all blog posts
@app.route("/api/posts", methods=["GET"])
def api_get_posts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT posts.id, posts.title, posts.content,
               posts.user_id, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """)
    posts = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(posts)
if __name__ == "__main__":
    app.run(debug=True)
    
# REST API - Get one blog post

@app.route("/api/posts/<int:post_id>", methods=["GET"])
def api_get_single_post(post_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT posts.id, posts.title, posts.content,
               posts.user_id, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.id = %s
    """, (post_id,))

    post = cursor.fetchone()

    cursor.close()
    db.close()

    if post:
        return jsonify(post)

    return jsonify({"message": "Blog post not found"}), 404

# REST API - Create a blog post

@app.route("/api/posts", methods=["POST"])
@login_required
def api_create_post():

    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"message": "Title and content are required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
        (session["user_id"], title, content)
    )

    db.commit()
    post_id = cursor.lastrowid

    cursor.close()
    db.close()

    return jsonify({
        "message": "Blog post created successfully",
        "post_id": post_id
    }), 201
    
# REST API - Update a blog post

@app.route("/api/posts/<int:post_id>", methods=["PUT"])
@login_required
def api_update_post(post_id):

    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"message": "Title and content are required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM posts WHERE id = %s AND user_id = %s",
        (post_id, session["user_id"])
    )

    post = cursor.fetchone()

    if not post:
        cursor.close()
        db.close()
        return jsonify({"message": "Post not found or access denied"}), 404

    cursor.execute(
        "UPDATE posts SET title = %s, content = %s WHERE id = %s",
        (title, content, post_id)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Blog post updated successfully"})



# REST API - Delete a blog post

@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
@login_required
def api_delete_post(post_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM posts WHERE id = %s AND user_id = %s",
        (post_id, session["user_id"])
    )

    post = cursor.fetchone()

    if not post:
        cursor.close()
        db.close()
        return jsonify({"message": "Post not found or access denied"}), 404

    cursor.execute(
        "DELETE FROM posts WHERE id = %s",
        (post_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Blog post deleted successfully"})


# REST API - Get comments for a blog post

@app.route("/api/posts/<int:post_id>/comments", methods=["GET"])
def api_get_comments(post_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM posts WHERE id = %s",
        (post_id,)
    )

    post = cursor.fetchone()

    if not post:
        cursor.close()
        db.close()
        return jsonify({"message": "Blog post not found"}), 404

    cursor.execute("""
        SELECT comments.id, comments.comment,
               comments.user_id, users.username,
               comments.created_at
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = %s
        ORDER BY comments.id DESC
    """, (post_id,))

    comments = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(comments)

# REST API - Add a comment to a blog post

@app.route("/api/posts/<int:post_id>/comments", methods=["POST"])
@login_required
def api_add_comment(post_id):

    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    comment = data.get("comment")

    if not comment or not comment.strip():
        return jsonify({"message": "Comment is required"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM posts WHERE id = %s",
        (post_id,)
    )

    post = cursor.fetchone()

    if not post:
        cursor.close()
        db.close()
        return jsonify({"message": "Blog post not found"}), 404

    cursor.execute(
        "INSERT INTO comments (post_id, user_id, comment) VALUES (%s, %s, %s)",
        (post_id, session["user_id"], comment.strip())
    )

    db.commit()
    comment_id = cursor.lastrowid

    cursor.close()
    db.close()

    return jsonify({
        "message": "Comment added successfully",
        "comment_id": comment_id
    }), 201