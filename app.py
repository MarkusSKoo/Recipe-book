import sqlite3
from flask import Flask, abort, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import db
import config
import recipes
import users
from datetime import timedelta

app = Flask(__name__)
app.secret_key = config.secret_key

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_recipes = recipes.get_recipes()
    return render_template("index.html", recipes=all_recipes)

@app.route("/find_recipe")
def find_recipe():
    query = request.args.get("query")
    if query:
        results = recipes.find_recipes(query)
    else:
        query = ""
        results = []
    return render_template("find_recipe.html", query=query, results=results)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    return render_template("show_recipe.html", recipe=recipe)

@app.route("/new_recipe")
def new_recipe():
    require_login()
    return render_template("new_recipe.html")

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    require_login()

    title = request.form["title"]
    description = request.form["description"]
    category = request.form["category"]
    ingredients = request.form["ingredients"]
    instructions = request.form["instructions"]

    if not all([title, description, category, ingredients, instructions]):
        return "VIRHE: Kaikki kentät ovat pakollisia"

    user_id = users.get_user_id(session["username"])
    if not user_id:
        return "VIRHE: Käyttäjää ei löydy"

    category_id = recipes.get_or_create_category(category)
    if not category_id:
        return "VIRHE: Kategorian lisääminen epäonnistui"

    recipes.add_recipe(user_id, title, description, category_id, ingredients, instructions)

    return redirect("/")

@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id):
    require_login()
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_recipe.html", recipe=recipe)

@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    require_login()

    recipe_id = request.form["recipe_id"]
    title = request.form["title"]
    description = request.form["description"]
    category = request.form["category"]
    ingredients = request.form["ingredients"]
    instructions = request.form["instructions"]

    if not all([title, description, category, ingredients, instructions]):
        return "VIRHE: Kaikki kentät ovat pakollisia"

    if not recipes.is_recipe_owner(recipe_id, session["user_id"]):
        abort(403)

    category_id = recipes.get_or_create_category(category)
    if not category_id:
        return "VIRHE: Kategorian lisääminen epäonnistui"

    recipes.update_recipe(recipe_id, title, description, category_id, ingredients, instructions)

    return redirect(f"/recipe/{recipe_id}")

@app.route("/remove_recipe/<int:recipe_id>")
def remove_recipe(recipe_id):
    require_login()
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    return render_template("remove_recipe.html", recipe=recipe)

@app.route("/remove_recipe", methods=["POST"])
def remove_recipe_post():
    if "username" not in session:
        return redirect("/login")

    recipe_id = request.form["recipe_id"]
    if "remove" in request.form:
        if not recipes.is_recipe_owner(recipe_id, session["user_id"]):
            abort(403)
        recipes.delete_recipe(recipe_id)
        return redirect("/")
    else:
        return redirect("/recipe/" + str(recipe_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or not password1 or not password2:
        return "VIRHE: Kaikki kentät ovat pakollisia"

    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    if len(password1) < 8:
        return "VIRHE: salasanan tulee olla vähintään 8 merkkiä pitkä"

    if len(username) > 20:
        return "VIRHE: käyttäjänimi on liian pitkä"

    if not username.isalnum():
        return "VIRHE: käyttäjänimi saa sisältää vain kirjaimia ja numeroita"

    password_hash = generate_password_hash(password1)

    try:
        users.create_user(username, password_hash)
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

        if not username or not password:
            return "VIRHE: Käyttäjänimi ja salasana ovat pakollisia"

        if len(username) > 50:
            return "VIRHE: käyttäjänimi on liian pitkä"

        if not username.isalnum():
            return "VIRHE: käyttäjänimi saa sisältää vain kirjaimia ja numeroita"

        user = users.get_user(username)
        if not user or not check_password_hash(user["password_hash"], password):
            return "VIRHE: väärä tunnus tai salasana"

        session.permanent = True
        session["user_id"] = user["id"]
        session["username"] = username
        return redirect("/")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
