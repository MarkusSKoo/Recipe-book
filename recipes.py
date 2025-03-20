import db

def add_recipe(user_id, title, description, category_id, ingredients, instructions):
    sql = """INSERT INTO recipes (user_id, title, description, category_id, ingredients, instructions)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, description, category_id, ingredients, instructions])
