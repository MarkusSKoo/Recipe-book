import secrets
from datetime import timedelta

from flask import Flask, abort, redirect, render_template, request, session, make_response, flash
import markupsafe

import config
import recipes
import users

app = Flask(__name__)
app.secret_key = config.secret_key

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    all_recipes = recipes.get_recipes()
    return render_template("index.html", recipes=all_recipes)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_recipes = users.get_recipes(user_id)
    return render_template("show_user.html", user=user, recipes=user_recipes)

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
    images = recipes.get_images(recipe_id)
    return render_template("show_recipe.html", recipe=recipe, classes=classes, comments=comments,
    average_rating=average_rating, images=images)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = recipes.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/new_recipe")
def new_recipe():
    require_login()
    classes = recipes.get_all_classes()
    return render_template("new_recipe.html", classes=classes)

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    require_login()
    check_csrf()

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
    check_csrf()

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
    check_csrf()

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

    return render_template("edit_recipe.html", recipe=recipe, classes=classes,
                           all_classes=all_classes)

@app.route("/images/<int:recipe_id>")
def edit_images(recipe_id):
    require_login()
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    images = recipes.get_images(recipe_id)

    return render_template("images.html", recipe=recipe, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()

    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith(".png"):
        flash("VIRHE: väärä tiedostomuoto")
        return redirect("/images/" + str(recipe_id))

    image = file.read()
    if len(image) > 100 * 1024:
        flash("VIRHE: liian suuri kuva")
        return redirect("/images/" + str(recipe_id))

    recipes.add_image(recipe_id, image)
    return redirect("/images/" + str(recipe_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()
    check_csrf()

    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        recipes.remove_image(recipe_id, image_id)

    return redirect("/images/" + str(recipe_id))

@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    require_login()
    check_csrf()

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

@app.route("/remove_recipe/<int:recipe_id>", methods=["GET", "POST"])
def remove_recipe(recipe_id):
    require_login()

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_recipe.html", recipe=recipe)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            recipes.remove_recipe(recipe_id)
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
        flash("VIRHE: kaikki kentät ovat pakollisia")
        return redirect("/register")

    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return redirect("/register")

    if len(password1) < 8:
        flash("VIRHE: salasanan tulee olla vähintään 8 merkkiä pitkä")
        return redirect("/register")

    if len(username) > 20:
        flash("VIRHE: käyttäjänimi on liian pitkä")
        return redirect("/register")

    if not username.isalnum():
        flash("VIRHE: käyttäjänimi saa sisältää vain kirjaimia ja numeroita")
        return redirect("/register")

    if not users.create_user(username, password1):
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")

    flash("Tunnus luotu")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("VIRHE: väärä tunnus tai salasana")
            return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
