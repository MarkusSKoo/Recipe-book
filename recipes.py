import db

def add_recipe(user_id, title, description, category_id, ingredients, instructions):
    sql = """INSERT INTO recipes (user_id, title, description, category_id, ingredients, instructions)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, description, category_id, ingredients, instructions])

def get_recipes():
    sql = "SELECT id, title FROM recipes ORDER BY id DESC"
    return db.query(sql)

def get_recipe(recipe_id):
    sql = """SELECT recipes.title,
                    recipes.description,
                    recipes.ingredients,
                    recipes.instructions,
                    recipes.category_id,
                    users.username
            FROM recipes, users
            WHERE recipes.user_id = users.id AND
            recipes.id = ?"""
    return db.query(sql, [recipe_id])[0]
