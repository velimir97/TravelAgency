from agency import db
from .models import UserModel, ArrangementModel
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    name_database = "travel_agency_database"
    con = psycopg2.connect(user='postgres', password='postgres', host='localhost')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = con.cursor()
    sql_create_database = "create database " + name_database + ";"
    cursor.execute(sql_create_database)
except Exception as e:
    print("Database " + name_database + " already exists")
    db.drop_all()

db.create_all()
#1
djole = UserModel(name="Dordje", surname="Vuckovic", email="djole53@vuk.com", username="vucko53", desired_type="guide", current_type="tourist")
djole.set_password("djole123")
db.session.add(djole)
db.session.commit()
#2
bole = UserModel(name="Bosko", surname="Djuric", email="boskic@dud.com", username="bor", desired_type="tourist", current_type="tourist")
bole.set_password("bole123")
db.session.add(bole)
db.session.commit()
#3
ana = UserModel(name="Ana", surname="Jakovljevic", email="ana@ba.com", username="anabanana", desired_type="guide", current_type="guide")
ana.set_password("ana123")
db.session.add(ana)
db.session.commit()
#4
maja = UserModel(name="Marija", surname="Kovacevic", email="maja@kovac.com", username="macika", desired_type="tourist", current_type="tourist")
maja.set_password("maja123")
db.session.add(maja)
db.session.commit()
#5
sanja = UserModel(name="Sanja", surname="Knezevic", email="sanja@knez.com", username="sanjica", desired_type="guide", current_type="tourist")
sanja.set_password("sanja123")
db.session.add(sanja)
db.session.commit()
#6
sara = UserModel(name="Sara", surname="Knezevic", email="sara@knez.com", username="saki", desired_type="admin", current_type="tourist")
sara.set_password("sara123")
db.session.add(sara)
db.session.commit()
#7
velja = UserModel(name="Velimir", surname="Bicanin", email="velimirbicanin@gmail.com", username="veljase", desired_type="admin", current_type="admin")
velja.set_password("velja123")
db.session.add(velja)
db.session.commit()
#8
ceca = UserModel(name="Svetlana", surname="Kovacevic", email="ceca53@kok.com", username="kocka", desired_type="tourist", current_type="tourist")
ceca.set_password("ceca123")
db.session.add(ceca)
db.session.commit()
#9
marko = UserModel(name="Marko", surname="Dunjic", email="mare@dunja.com", username="dunja", desired_type="guide", current_type="guide")
marko.set_password("marko123")
db.session.add(marko)
db.session.commit()
#10
teodora = UserModel(name="Teodora", surname="Pribanovic", email="teda@mi.com", username="titi", desired_type="tourist", current_type="tourist")
teodora.set_password("teda123")
db.session.add(teodora)
db.session.commit()

#1
engleska = ArrangementModel(start_date = datetime.now() + timedelta(days=100),
                           end_date = datetime.now() + timedelta(days=110),
                           description = "English pub",
                           destination = "English, London",
                           number_of_seats = 55,
                           free_seats = 55,
                           price = 555,
                           admin_id = 7
)
engleska.guide = ana
db.session.add(engleska)
db.session.commit()
#2
francuska = ArrangementModel(start_date = datetime.now() + timedelta(days= 40),
                           end_date = datetime.now() + timedelta(days=45),
                           description = "Jelisejska polja",
                           destination = "Francuska, Pariz",
                           number_of_seats = 40,
                           free_seats = 40,
                           price = 453,
                           admin_id = 7
)
db.session.add(francuska)
db.session.commit()
#3
spanija = ArrangementModel(start_date = datetime.now() + timedelta(days=4),
                           end_date = datetime.now() + timedelta(days=8),
                           description = "Park of Antonio Gaudi",
                           destination = "Spain, Barselona",
                           number_of_seats = 10,
                           free_seats = 10,
                           price = 355,
                           admin_id = 7
)
spanija.guide = ana
db.session.add(spanija)
db.session.commit()
#4
ceska = ArrangementModel(start_date = datetime.now() + timedelta(days=3),
                           end_date = datetime.now() + timedelta(days=13),
                           description = "Visit to Adam Ondra",
                           destination = "Ceska, Brno",
                           number_of_seats = 3,
                           free_seats = 3,
                           price = 100,
                           admin_id = 7
)
db.session.add(ceska)
db.session.commit()
#5
nemacka = ArrangementModel(start_date = datetime.now() + timedelta(days=55),
                           end_date = datetime.now() + timedelta(days=65),
                           description = "Bridges of Hamburh",
                           destination = "Nemacka, Hamburg",
                           number_of_seats = 112,
                           free_seats = 112,
                           price = 420,
                           admin_id = 7
)
nemacka.guide = ana
db.session.add(nemacka)
db.session.commit()
#6
rusija = ArrangementModel(start_date = datetime.now() + timedelta(days=20),
                           end_date = datetime.now() + timedelta(days=32),
                           description = "Crveni trg",
                           destination = "Rusija, Moskva",
                           number_of_seats = 24,
                           free_seats = 24,
                           price = 100,
                           admin_id = 7
)
db.session.add(rusija)
rusija.tourists.append(maja)
rusija.tourists.append(djole)
rusija.tourists.append(bole)
db.session.commit()
#7
cg = ArrangementModel(start_date = datetime.now() + timedelta(days=250),
                           end_date = datetime.now() + timedelta(days=260),
                           description = "More",
                           destination = "Crna Gora, Sveti Stefan",
                           number_of_seats = 4,
                           free_seats = 4,
                           price = 245,
                           admin_id = 7
)
db.session.add(cg)
db.session.commit()
#8
srbija1 = ArrangementModel(start_date = datetime.now() + timedelta(days=90),
                           end_date = datetime.now() + timedelta(days=120),
                           description = "Skiing",
                           destination = "Serbia, Kopaonik",
                           number_of_seats = 6,
                           free_seats = 3,
                           price = 500,
                           admin_id = 7
)
db.session.add(srbija1)
srbija1.tourists.append(djole)
srbija1.tourists.append(bole)
srbija1.tourists.append(maja)
db.session.commit()
#9
srbija2 = ArrangementModel(start_date = datetime.now() + timedelta(days=10),
                           end_date = datetime.now() + timedelta(days=11),
                           description = "Planinarenje",
                           destination = "Serbia, Stara planina",
                           number_of_seats = 3,
                           free_seats = 0,
                           price = 10,
                           admin_id = 7
)
db.session.add(srbija2)
srbija2.tourists.append(ana)
srbija2.tourists.append(velja)
srbija2.tourists.append(ceca)
db.session.commit()

#10
srbija3 = ArrangementModel(start_date = datetime.now() - timedelta(days=10),
                           end_date = datetime.now() - timedelta(days=5),
                           description = "Planinarenje",
                           destination = "Serbia, Zeljin",
                           number_of_seats = 3,
                           free_seats = 0,
                           price = 10,
                           admin_id = 7
)
db.session.add(srbija3)
srbija3.guide = marko
srbija3.tourists.append(ana)
srbija3.tourists.append(velja)
srbija3.tourists.append(ceca)
db.session.commit()