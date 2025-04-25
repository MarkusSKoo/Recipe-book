import db

def recipe_count():
    sql = "SELECT COUNT(*) FROM recipes"
    result = db.query(sql)
    return result[0][0]

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def get_classes(recipe_id):
    sql = "SELECT title, value FROM recipe_classes WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def add_recipe(title, description, ingredients, instructions, user_id, classes):
    sql = """INSERT INTO recipes (title, description, ingredients, instructions, user_id)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, ingredients, instructions, user_id])

    recipe_id = db.last_insert_id()

    sql = "INSERT INTO recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [recipe_id, class_title, class_value])

    return recipe_id

def add_comment(recipe_id, user_id, comment):
    sql = "INSERT INTO comments (recipe_id, user_id, comment) VALUES (?, ?, ?)"
    db.execute(sql, [recipe_id, user_id, comment])
    return recipe_id

def get_comments(recipe_id):
    sql = """SELECT comment, users.id user_id, users.username
            FROM comments, users
            WHERE comments.recipe_id = ? AND comments.user_id = users.id
            ORDER BY comments.id DESC"""
    return db.query(sql, [recipe_id])

def add_rating(recipe_id, user_id, rating):
    sql = """INSERT INTO ratings (recipe_id, user_id, rating)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, recipe_id) DO UPDATE SET rating=excluded.rating"""
    db.execute(sql, [recipe_id, user_id, rating])

def get_average_rating(recipe_id):
    sql = "SELECT AVG(rating) AS rating FROM ratings WHERE recipe_id = ?"
    result = db.query(sql, [recipe_id])
    if result[0]["rating"]:
        return round(result[0]["rating"], 2)
    return 0.0

def get_images(recipe_id):
    sql = "SELECT id FROM images WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def add_image(recipe_id, image):
    sql = "INSERT INTO images (recipe_id, image) VALUES (?, ?)"
    db.execute(sql, [recipe_id, image])

def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(recipe_id, image_id):
    sql = "DELETE FROM images WHERE id = ? AND recipe_id = ?"
    db.execute(sql, [image_id, recipe_id])

def get_recipes(page, page_size):
    sql = """SELECT recipes.id,
               recipes.title,
               users.id AS user_id,
               users.username,
               COUNT(ratings.id) AS ratings_count,
               ROUND(AVG(ratings.rating), 1) AS average_rating,
               COUNT(recipes.id) total
        FROM recipes
        JOIN users ON recipes.user_id = users.id
        LEFT JOIN ratings ON recipes.id = ratings.recipe_id
        GROUP BY recipes.id, users.id
        ORDER BY recipes.id DESC
        LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])


def get_recipe(recipe_id):
    sql = """SELECT recipes.id,
                    recipes.title,
                    recipes.description,
                    recipes.ingredients,
                    recipes.instructions,
                    users.id user_id,
                    users.username
            FROM recipes
            JOIN users ON recipes.user_id = users.id
            WHERE recipes.id = ?"""
    result = db.query(sql, [recipe_id])
    return result[0] if result else None

def update_recipe(recipe_id, title, description, ingredients, instructions, classes):
    sql = """UPDATE recipes SET title = ?,
                                description = ?,
                                ingredients = ?,
                                instructions = ?
                            WHERE id = ?"""
    db.execute(sql, [title, description, ingredients, instructions, recipe_id])

    sql = "DELETE FROM recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "INSERT INTO recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [recipe_id, class_title, class_value])

def remove_recipe(recipe_id):
    sql = "DELETE FROM ratings WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM comments WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM images WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def find_recipes(query):
    sql = """SELECT id, title
            FROM recipes
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])
