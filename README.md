# Recipe-book

## Sovelluksen toiminnot

*  Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee kuvaus, tarvittavat ainekset ja valmistusohje.
*  Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
*  Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan reseptejä.
*  Käyttäjä pystyy lisäämään reseptiin kuvia ja poistamaan niitä.
*  Käyttäjä näkee sovellukseen lisätyt reseptit.
*  Käyttäjä pystyy etsimään reseptejä hakusanalla.
*  Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, tulinen, vegaaninen).
*  Käyttäjäsivu näyttää montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
*  Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.
 
## sovelluksen asennus

Asenna 'flask'-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```
## sovelluksen testaaminen suurilla tietomäärillä

Sovellusta testattu suurilla tietomäärillä seed.py-tiedoston kautta, jonka sisältö on seuraavanlainen:

```
import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM categories")
db.execute("DELETE FROM classes")
db.execute("DELETE FROM recipe_classes")
db.execute("DELETE FROM recipes")
db.execute("DELETE FROM comments")
db.execute("DELETE FROM ratings")
db.execute("DELETE FROM images")

db.execute("""INSERT INTO classes (title, value) VALUES
('Ruokalaji', 'Alkuruoka'),
('Ruokalaji', 'Pääruoka'),
('Ruokalaji', 'Jälkiruoka'),

('Ruokarajoitus', 'Ei rajoitusta'),
('Ruokarajoitus', 'Kasvisruoka'),
('Ruokarajoitus', 'Vegaaninen'),

('Tulisuus', 'Ei tulinen'),
('Tulisuus', 'Mieto'),
('Tulisuus', 'Tulinen');""")

user_count = 1000
recipe_count = 10**5
comment_count = 10**6

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               ["user" + str(i), 123123])

for i in range(1, recipe_count + 1):
    user_id = random.randint(1, user_count)
    result = db.execute("INSERT INTO recipes (user_id, title, description, ingredients, instructions) VALUES (?, ?, ?, ?, ?)",
               [user_id, "thread" + str(i), str(i), str(i), str(i)])
    
    recipe_id = result.lastrowid
    
    sql = "INSERT INTO recipe_classes (recipe_id, title, value) VALUES (?, ?, ?), (?, ?, ?), (?, ?, ?)"
    db.execute(sql, [recipe_id, "Ruokalaji", "Pääruoka", recipe_id, "Ruokarajoitus", "Kasvisruoka", recipe_id, "Tulisuus", "Mieto"])

for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    recipe_id = random.randint(1, recipe_count)
    db.execute("""INSERT INTO comments (recipe_id, user_id, comment)
                  VALUES (?, ?, ?)""",
               [recipe_id, user_id, "message" + str(i)])

db.commit()
db.close()
```

Sovellus avautuu nopeasti myös suurilla tietomäärillä.
