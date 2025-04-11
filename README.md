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
