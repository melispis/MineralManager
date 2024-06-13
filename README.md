# MineralManager
#### Video Demo:  <https://www.youtube.com/watch?v=-xClcPePsJw>
#### Description: MineralManager is a web-based application to keep track of your personal mineral collection. Make and edit collections of your favorite gems and minerals. Or other stuff if you like!
#
### Beschrijving en belangrijkste functionaliteiten:
MineralManager is een web-based applicatie voor het bijhouden van collecties van dingen die je leuk vind. Wanneer je veel dingen hebt en graag wat meer overzicht wilt over je spullen, kun je gebruikmaken van mineralmanager. Een collectie heeft een titel en een beschrijving. In de collectie kun je foto's uploaden van de dingen die je erin wilt. Bij elke foto is een titel verplicht, optioneel kun je ook nog een beschrijving toevoegen. Bij het verzamelen van mineralen is het bijvoorbeeld leuk om een uitgebreide beschrijving toe te voegen over de herkomst van het mineraal. Als je klaar bent verschijnt je collectie in het overzicht. Je kunt op elk moment collecties toevoegen of verwijderen, of items uit je collectie toevoegen of verwijderen. Als je een foutje hebt gemaakt, of je collectie is veranderd, kun je de titel en/of beschrijving gemakkelijk aanpassen. Ook bij de items is het mogelijk om achteraf de informatie aan te passen.
#
### Extra functies:
Functies die de web applicatie compleet maken zijn het aanmaken van je eigen account en het inloggen in je bestaande account, zodat je altijd terug kunt naar de collecties die aan je account gelinkt zijn. Op je profiel kun je je eigen profielfoto instellen als je dat leuk vind, anders staat er een standaard user foto. Ook kun je je wachtwoord veranderen mocht je dat willen. De applicatie houdt bij het aanmaken van een account rekening met bestaande accounts, waardoor je een username maar 1x kunt gebruiken. Op deze manier heeft iedereen een unieke username.
#
### Ontwerp keuzes:
Ik vond het belangrijk om de gebruiker zo veel mogelijk vrijheid te geven in de mogelijkheden en de navigatie zo vanzelfsprekend mogelijk te maken. Om dat te doen heb ik ervoor gezorgd dat je kunt toevoegen, verwijderen en aanpassen, zo vaak als nodig is, en dit op dezelfde plek te plaatsen voor consistentie. Om het verder te personaliseren heb ik de gebruiker de mogelijkheid gegeven om een profielfoto in te stellen, dit motiveert de gebruiker nog meer om gebruik te maken van de applicatie. De website is zo simpel mogelijk gebouwd met behulp van bootstrap, zodat het niet afleidt van de hoofd functionaliteit en overzichtelijk blijft.
#
### Technische info
De applicatie is gebouwd met flask. In app.py vind je alle routes voor het gebruiken van de applicatie. Bijvoorbeeld login, register, change-password, add-collection, delete-collection, add-images, edit-collection, en dergelijke. In helpers.py staan twee helper functies zoals een login_required decorator, die gebruikt word in app.py. De HTML maakt gebruik van de Bootstrap library voor een deel van de styling van de webpagina, waardoor het ook responsive is. De templates voor elke pagina kun je vinden in de map 'templates'. Alle informatie over users, collecties en images word opgeslagen in de database, met behulp van SQLite3. De images worden geupload in static/uploads
#
## Functies:
#
### def inject_profile_picture()
Deze context processor haalt de ingestelde profielfoto op van de user uit de database, als deze er is, en maakt deze variabele beschikbaar voor alle templates.
#
### def register()
Deze route rendert de registreer pagina, en haalt bij een POST request de benodigde data uit het formulier om een account aan te maken in de database. Ook voert hij controles uit zoals een missende username of password, of de username niet al bestaat, en of de wachtwoorden matchen. Daarna maakt hij een hash aan van het wachtwoord en word deze samen met de username in de database ge-insert. Na het registreren volgt een success flash message en word de user geredirect naar zijn profiel.
#
### def login()
Deze functie onder de login route rendert de login pagina. Bij een POST request haalt hij de username en wachtwoord op, controleert deze op volledigheid en/of fouten en onthoud hij de sessie. Vervolgens haalt hij de collecties op door user albums die gelinkt zijn aan deze user op te halen als deze bestaan om de eerste image van dit album te displayen, en de hoeveelheid items in de collectie. Deze info word tijdens het renderen aan de template toegevoegd.
#
### def logout()
De logout functie cleared de huidige sessie en redirect de user naar de startpagina (index).
#
### def profile()
De functie onder de route /profile haalt de huidige user id en user albums op. Om de collecties te laten zien haalt hij de eerste image voor elke collectie en het totaal aantal items uit de database met for loops. Daarna rendert hij de profiel template met deze informatie.
#
### def settings()
Op de settings pagina word de user id en de profielfoto opgehaald om te laten zien op de pagina. Ook staat hier de functie om je profielfoto te uploaden. Het uploaden houdt rekening met veiligheid door de flask functie allowed_file(). De foto word opgeslagen in de map 'uploads'. Ook haalt hij de username van de gebruiker uit de database om te laten zien in de html.
#
### def upload_files()
Onder de route new collection heb je de functie om een nieuwe collectie aan te maken en bestanden te uploaden als items in je collectie. De functie haalt de benodigde info zoals titel en beschrijving uit het formulier. Deze info word in de database gekoppeld aan de user_id. Ook slaan we de aanmaakdatum en tijd op met datetime.now(). Voor de bestanden halen we de files, titles en descriptions eerst op, en loopen er daarna overheen om voor elke image een nieuwe naam aan te maken (om duplicates te voorkomen), op te slaan in 'uploads', en daarna alle details op te slaan in een andere tabel genaamd user images. De images zijn gekoppeld aan de collectie database met het album_id. Na de uitvoering wordt de gebruiker geredirect naar zijn profiel met een successmessage, en ziet hij zijn nieuwe collectie.
#
### def download_file()
Download functie volgens de Flask documentatie.
#
### def change_password()
De gebruiker krijgt de mogelijkheid om zijn wachtwoord aan te passen. Dit kan hij doen op de settings pagina. Wanneer dit formulier word verstuurd word de actie '/change_password' uitgevoerd. De informatie word uit het formulier gehaald en gecheckt. De extra password requirements zijn in deze versie uitgecomment, maar zorgen voor een aantal regels zoals wachtwoord lengte, speciale tekens, cijfers en hoofdletters. Wanneer alles klopt word een nieuwe hash aangemaakt en in de database geupdate voor de huidige user_id.
#
### def view_collection(collection_id)
De detail pagina van de collectie. Bij het aanklikken word de collectie id meegegeven in de url, en in de route gebruikt om de juiste collectie op te halen in de database met de get_collection() functie. De items worden opgehaald uit album_images met get_images(), en de titel en beschrijving van de collectie. Deze worden gerendered in de view-collection template.
### def get_collection(collection_id)
Deze functie in dezelfde route haalt de collectie op uit de database aan de hand van de meegegeven collection_id en deze variabele word gereturned.
### def get_images(collection_id)
Een lijst van foto's uit de collectie word opgehaald met een database query aan de hand van de meegegeven collection_id.
#
### def delete_collection(collection_id)
Met deze functie kan de user een collectie verwijderen. Aan de hand van de meegegeven id word een delete query uitgevoerd in de database. Eerst op de foto's, zodat deze niet blijven bestaan, daarna de user_albums info.
#
### def edit_collection(collection_id)
De gebruiker kan de informatie van de collectie aanpassen. De nieuwe titel en/of beschrijving word opgehaald en met de juiste user_id en meegegeven collection_id geupdate in de database met een update query.
#
### def add_images(collection_id)
Als de gebruiker na het aanmaken van de collectie nog meer items wilt toevoegen maakt hij gebruik van deze functie. We halen we de files, titles en descriptions eerst op, en loopen er daarna overheen om voor elke image een nieuwe naam aan te maken (om duplicates te voorkomen), op te slaan in 'uploads', en daarna alle details op te slaan in een andere tabel genaamd user images. De images zijn gekoppeld aan de collectie database met het album_id. Na de uitvoering wordt de gebruiker geredirect naar zijn de collectie met een successmessage, en ziet hij zijn nieuwe items.
#
### def view_image(image_id)
Detail pagina van een item uit een collectie. Hier ziet de gebruiker de titel en beschrijving en kan hij hem aanpassen of verwijderen. De functie haalt de foto op aan de hand van de meegegeven image_id en pakt de filename om die mee te geven in de template zodat hij daar in de <img> kan worden geplaatst.
#
### def delete_image(image_id)
Deze functie verwijdert een foto en bijbehorende info uit de database. De collectie waarin de foto in staat word opgehaald aan de hand van de meegegeven image_id zodat de user geredirect kan worden naar deze collectie na het uitvoeren van de deletion. Daarna word de delete query uitgevoerd op de database, die de hele row die hoort bij de image_id verwijdert.
#
### def edit_image(image_id)
Op de edit image template kan de gebruiker de titel en beschrijving aanpassen. De functie haalt deze waardes op in new_title en new_description en update deze values in de database voor de meegegeven image_id.
#
<sub>CS50 final project</sub>