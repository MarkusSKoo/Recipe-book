import sqlite3
from flask import Flask, abort, redirect, render_template, request, session
import db
import config
import recipes
import users
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash

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

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user_info(user_id)
    if not user:
        abort(404)
    recipes = users.get_recipes(user_id )
    return render_template("show_user.html", user=user, recipes=recipes)

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
    classes = recipes.get_classes(recipe_id)
    comments = recipes.get_comments(recipe_id)
    average_rating = recipes.get_average_rating(recipe_id)
    return render_template("show_recipe.html", recipe=recipe, classes=classes, comments=comments, average_rating=average_rating)

@app.route("/new_recipe")
def new_recipe():
    require_login()
    classes = recipes.get_all_classes()
    return render_template("new_recipe.html", classes=classes)

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    require_login()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    ingredients = request.form["ingredients"]
    if not ingredients or len(ingredients) > 1000:
        abort(403)
    instructions = request.form["instructions"]
    if not instructions or len(instructions) > 5000:
        abort(403)
    user_id = session["user_id"]

    all_classes = recipes.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    recipe_id = recipes.add_recipe(title, description, ingredients, instructions, user_id, classes)

    return redirect("/recipe/" + str(recipe_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()

    comment = request.form["comment"]
    if not comment or len(comment) > 1000:
        abort(403)

    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(403)

    user_id = session["user_id"]
    if not user_id:
        abort(403)

    recipe_id = recipes.add_comment(recipe_id, user_id, comment)

    return redirect("/recipe/" + str(recipe_id))

@app.route("/rate_recipe", methods=["POST"])
def rate_recipe():
    require_login()
    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(403)

    rating = int(request.form["rating"])
    if not rating or rating < 1 or rating > 5:
        abort(403)

    user_id = session["user_id"]
    if not user_id:
        abort(403)

    recipes.add_rating(recipe_id, user_id, rating)
    return redirect("/recipe/" + str(recipe_id))

@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id):
    require_login()
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    all_classes = recipes.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in recipes.get_classes(recipe_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_recipe.html", recipe=recipe, classes=classes, all_classes=all_classes)

@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    require_login()

    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(403)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    ingredients = request.form["ingredients"]
    if not ingredients or len(ingredients) > 1000:
        abort(403)
    instructions = request.form["instructions"]
    if not instructions or len(instructions) > 5000:
        abort(403)

    all_classes = recipes.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    recipes.update_recipe(recipe_id, title, description, ingredients, instructions, classes)

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

    if not users.create_user(username, password1):
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
