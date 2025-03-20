import db

def add_recipe(user_id, title, description, category_id, ingredients, instructions):
    sql = """INSERT INTO recipes (user_id, title, description, category_id, ingredients, instructions)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, description, category_id, ingredients, instructions])

def get_recipes():
    sql = "SELECT id, title FROM recipes ORDER BY id DESC"
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

def update_recipe(recipe_id, title, description, ingredients, instructions, category):
    sql = """UPDATE recipes SET title = ?,
                                description = ?,
                                ingredients = ?,
                                instructions = ?,
                                category = ?
                            WHERE id = ?"""
    db.execute(sql, [title, description, ingredients, instructions, category, recipe_id])
