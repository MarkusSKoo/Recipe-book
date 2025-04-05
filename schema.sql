CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE recipe_classes (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes,
    title TEXT,
    value TEXT
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    ingredients TEXT,
    instructions TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER,
    user_id INTEGER,
    comment TEXT,
    rating INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
