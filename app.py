import sqlite3
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import db
import config
import recipes

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_recipes = recipes.get_recipes()
    return render_template("index.html", recipes=all_recipes)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    return render_template("show_recipe.html", recipe=recipe)

@app.route("/new_recipe")
def new_recipe():
    return render_template("new_recipe.html")

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    if "username" not in session:
        return redirect("/login")

    title = request.form["title"]
    description = request.form["description"]
    category = request.form["category"]
    ingredients = request.form["ingredients"]
    instructions = request.form["instructions"]

    user_id_query = "SELECT id FROM users WHERE username = ?"
    user_id_result = db.query(user_id_query, [session["username"]])
    if not user_id_result:
        return "VIRHE: Käyttäjää ei löydy"
    user_id = user_id_result[0]["id"]

    category_id_query = "SELECT id FROM categories WHERE name = ?"
    category_id_result = db.query(category_id_query, [category])
    print(f"Category query result: {category_id_result}")
    if not category_id_result:
        insert_category_query = "INSERT INTO categories (name) VALUES (?)"
        db.execute(insert_category_query, [category])
        category_id_result = db.query(category_id_query, [category])
        if not category_id_result:
            return "VIRHE: Kategorian lisääminen epäonnistui"
    category_id = category_id_result[0]["id"]

    recipes.add_recipe(user_id, title, description, category_id, ingredients, instructions)

    print(f"Received form data: title={title}, description={description}, category={category}, ingredients={ingredients}, instructions={instructions}")

    return redirect("/")

@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    return render_template("edit_recipe.html", recipe=recipe)

@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    if "username" not in session:
        return redirect("/login")

    recipe_id = request.form["recipe_id"]
    title = request.form["title"]
    description = request.form["description"]
    category = request.form["category"]
    ingredients = request.form["ingredients"]
    instructions = request.form["instructions"]

    user_id_query = "SELECT user_id FROM recipes WHERE id = ?"
    user_id_result = db.query(user_id_query, [recipe_id])
    if not user_id_result or user_id_result[0]["user_id"] != session["user_id"]:
        return "VIRHE: Sinulla ei ole oikeutta muokata tätä reseptiä"

    category_id_query = "SELECT id FROM categories WHERE name = ?"
    category_id_result = db.query(category_id_query, [category])
    if not category_id_result:
        insert_category_query = "INSERT INTO categories (name) VALUES (?)"
        db.execute(insert_category_query, [category])
        category_id_result = db.query(category_id_query, [category])
        if not category_id_result:
            return "VIRHE: Kategorian lisääminen epäonnistui"
    category_id = category_id_result[0]["id"]

    update_query = """
    UPDATE recipes
    SET title = ?, description = ?, category_id = ?, ingredients = ?, instructions = ?
    WHERE id = ?
    """
    db.execute(update_query, [title, description, category_id, ingredients, instructions, recipe_id])

    return redirect(f"/recipe/{recipe_id}")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])

        if not result:
            return "VIRHE: väärä tunnus tai salasana"

        user_id = result[0]["id"]
        password_hash = result[0]["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
