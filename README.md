# Recipe-book

*  Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
*  Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
*  Käyttäjä pystyy lisäämään reseptejä ja muokkaamaan ja poistamaan niitä.
*  Käyttäjä näkee sovellukseen lisätyt reseptit.
*  Käyttäjä pystyy etsimään reseptejä hakusanalla.
*  Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, intialainen, vegaaninen).
*  Tulossa myöhemmin:
      *  Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
      *  Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.
 
* Ohjeet sovelluksen käynnistämiseen:
     * Avaa komentoikkuna ja kloonaa repository koneellesi komennolla "git clone https://github.com/MarkusSKoo/Recipe-book.git" haluamaasi hakemistoon
     * Avaa recipe-book -kansio komennolla "cd Recipe-book"
     * Asenna virtuaaliympäristö komennolla "python -m venv myenv"
     * Aktivoi virtuaaliympäristö
            * Macbook:illa/Linux:lla: "source myenv/bin/activate"
            * Windowsilla: "myenv\Scripts\activate"
     * Asenna Flask tarvittaessa komennolla "pip install Flask"
     * Tarvittavien asennusten jälkeen aja flask run-komento
     * kopioi komentoriville tuleva osoite selaimesi ikkunaan ja avaa sovellus
