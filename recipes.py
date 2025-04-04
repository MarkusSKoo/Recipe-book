import db

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
    

def get_recipes():
    sql = "SELECT id, title, user_id FROM recipes ORDER BY id DESC"
    return db.query(sql)

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

def delete_recipe(recipe_id):
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

def get_or_create_category(name):
    category_id_query = "SELECT id FROM categories WHERE name = ?"
    category_id_result = db.query(category_id_query, [name])
    if not category_id_result:
        insert_category_query = "INSERT INTO categories (name) VALUES (?)"
        db.execute(insert_category_query, [name])
        category_id_result = db.query(category_id_query, [name])
    return category_id_result[0]["id"] if category_id_result else None

def is_recipe_owner(recipe_id, user_id):
    user_id_query = "SELECT user_id FROM recipes WHERE id = ?"
    user_id_result = db.query(user_id_query, [recipe_id])
    return user_id_result and user_id_result[0]["user_id"] == user_id