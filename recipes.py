import db

def add_recipe(user_id, title, description, category_id, ingredients, instructions):
    sql = """INSERT INTO recipes (user_id, title, description, category_id, ingredients, instructions)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, description, category_id, ingredients, instructions])

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
                    categories.name AS category,
                    users.username
            FROM recipes
            JOIN users ON recipes.user_id = users.id
            JOIN categories ON recipes.category_id = categories.id
            WHERE recipes.id = ?"""
    return db.query(sql, [recipe_id])[0]

def update_recipe(recipe_id, title, description, category_id, ingredients, instructions):
    sql = """UPDATE recipes SET title = ?,
                                description = ?,
                                category_id = ?,
                                ingredients = ?,
                                instructions = ?
                            WHERE id = ?"""
    db.execute(sql, [title, description, category_id, ingredients, instructions, recipe_id])

def delete_recipe(recipe_id):
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