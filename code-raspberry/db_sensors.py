import sqlite3
import datetime
import time
# Créé une base de données et défini des données
path = 'db_sensors.db'

def addData (name,date,value,greenhouse):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connexion.cursor()
        print("Connected to SQLite")

        #setUp_Table ='''CREATE TABLE IF NOT EXISTS tab_sensor_data_test( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT, date timestamp, value REAL, greenhouse TEXT);'''
        setUp_Table ='''CREATE TABLE IF NOT EXISTS tab_sensor_data_test( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT, date TEXT, value REAL, greenhouse TEXT);'''

        cursor.execute(setUp_Table)
        insert_data = '''INSERT INTO tab_sensor_data_test(name, date, value, greenhouse) VALUES(?,?,?,?) WITH nolock;'''
        data_tuples = (name,date,value,greenhouse)
        cursor.execute(insert_data,data_tuples)
        connexion.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

# Récupère toutes les données de la base de données
def getDataAll ():
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connexion.cursor()
        print("Connected to SQLite")
        selected_query = '''SELECT * FROM tab_sensor_data_test'''
        cursor.execute(selected_query)
        rows = cursor.fetchall()
        print("id | name | date | value | greenhouse")
        for row in rows:
            id = row[0]
            name = row[1]
            date = row[2]
            value = row[3]
            greenhouse = row[4]
            print(id, " | ", name, " | ",date, " | ",value, " | ",greenhouse)
        cursor.close()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

# Récupère les données d'un capteur en particulier
def getDataName (name):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connexion.cursor()
        print("Connected to SQLite")
        selected_query = '''SELECT * FROM tab_sensor_data_test WHERE name = ?'''
        cursor.execute(selected_query,(name,))
        rows = cursor.fetchall()
        print("where name = ",name," :\n")
        print("id | name | date | value | greenhouse")
        for row in rows:
            id = row[0]
            name = row[1]
            date = row[2]
            value = row[3]
            greenhouse = row[4]
            print(id, " | ", name, " | ",date, " | ",value, " | ",greenhouse)
        cursor.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

#récupère les données entre deux dates
def getDataDate (start_date,end_date):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connexion.cursor()
        print("Connected to SQLite")
        selected_query = '''SELECT * FROM tab_sensor_data_test WHERE date BETWEEN ? AND ?'''
        cursor.execute(selected_query,(start_date,end_date))
        rows = cursor.fetchall()
        print("where date between ",start_date," and ",end_date," :\n")
        print("id | name | date | value | greenhouse")
        for row in rows:
            id = row[0]
            name = row[1]
            date = row[2]
            value = row[3]
            greenhouse = row[4]
            print(id, " | ", name, " | ",date, " | ",value, " | ",greenhouse)
        cursor.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

#récupère les données entre deux valeurs d'un capteur en particulier
def getDataValue (name, value_min, value_max):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connexion.cursor()
        print("Connected to SQLite")
        selected_query = '''SELECT * FROM tab_sensor_data_test WHERE name = ? AND value BETWEEN ? AND ?'''
        cursor.execute(selected_query,(name,value_min,value_max))
        rows = cursor.fetchall()
        print("where name = ",name," and value between ",value_min," and ",value_max," :\n")
        print("id | name | date | value | greenhouse")
        for row in rows:
            id = row[0]
            name = row[1]
            date = row[2]
            value = row[3]
            greenhouse = row[4]
            print(id, " | ", name, " | ",date, " | ",value , " | ",greenhouse)
        cursor.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

#supprime toutes les données de la base de données
def clearData ():
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connexion.cursor()
        print("Connected to SQLite")
        selected_query = '''DELETE FROM tab_sensor_data_test'''
        cursor.execute(selected_query)
        connexion.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")
    
#ajout de datadummies

def addDummies():
    
    addData("anemometre",'2023-10-24 14:55:04.320',25.0,'grange')

#grange
    #anemometre
def addDummies():
    addData("anemometre",'2023-10-23 10:55:04.320',25.0,'grange')
    addData("anemometre",'2023-10-23 12:55:04.320',28.0,'grange')
    addData("anemometre",'2023-10-23 14:55:04.320',31.0,'grange')
    addData("anemometre",'2023-10-23 16:55:04.320',35.0,'grange')
    addData("anemometre",'2023-10-23 18:55:04.320',38.0,'grange')
    addData("anemometre",'2023-10-23 20:55:04.320',39.0,'grange')
    addData("anemometre",'2023-10-23 22:55:04.320',40.0,'grange')
    addData("anemometre",'2023-10-24 0:55:04.320',40.0,'grange')
    addData("anemometre",'2023-10-24 2:55:04.320',38.0,'grange')
    addData("anemometre",'2023-10-24 4:55:04.320',36.0,'grange')
    addData("anemometre",'2023-10-24 6:55:04.320',33.0,'grange')
    addData("anemometre",'2023-10-24 8:55:04.320',29.0,'grange')
    addData("anemometre",'2023-10-24 10:55:04.320',23.0,'grange')
    addData("anemometre",'2023-10-24 12:55:04.320',20.0,'grange')
    addData("anemometre",'2023-10-24 14:55:04.320',19.0,'grange')
    

    #serre 1
        #temperature
    addData("temperature",'2023-10-23 10:55:04.320',25.0,'serre_1')
    addData("temperature",'2023-10-23 12:55:04.320',32.0,'serre_1')
    addData("temperature",'2023-10-23 14:55:04.320',18.0,'serre_1')
    addData("temperature",'2023-10-23 16:55:04.320',21.0,'serre_1')
    addData("temperature",'2023-10-23 18:55:04.320',28.0,'serre_1')
    addData("temperature",'2023-10-23 20:55:04.320',25.0,'serre_1')
    addData("temperature",'2023-10-23 22:55:04.320',18.0,'serre_1')
    addData("temperature",'2023-10-24 0:55:04.320',22.0,'serre_1')
    addData("temperature",'2023-10-24 2:55:04.320',25.0,'serre_1')
    addData("temperature",'2023-10-24 4:55:04.320',18.0,'serre_1')
    addData("temperature",'2023-10-24 6:55:04.320',22.0,'serre_1')
    addData("temperature",'2023-10-24 8:55:04.320',25.0,'serre_1')
    addData("temperature",'2023-10-24 10:55:04.320',18.0,'serre_1')
    addData("temperature",'2023-10-24 12:55:04.320',22.0,'serre_1')
    addData("temperature",'2023-10-24 14:55:04.320',25.0,'serre_1')
        #humidite
    addData("humidite",'2023-10-23 10:55:04.320',25.0,'serre_1')
    addData("humidite",'2023-10-23 12:55:04.320',32.0,'serre_1')
    addData("humidite",'2023-10-23 14:55:04.320',18.0,'serre_1')
    addData("humidite",'2023-10-23 16:55:04.320',21.0,'serre_1')
    addData("humidite",'2023-10-23 18:55:04.320',28.0,'serre_1')
    addData("humidite",'2023-10-23 20:55:04.320',25.0,'serre_1')
    addData("humidite",'2023-10-23 22:55:04.320',18.0,'serre_1')
    addData("humidite",'2023-10-24 0:55:04.320',22.0,'serre_1')
    addData("humidite",'2023-10-24 2:55:04.320',25.0,'serre_1')
    addData("humidite",'2023-10-24 4:55:04.320',18.0,'serre_1')
    addData("humidite",'2023-10-24 6:55:04.320',22.0,'serre_1')
    addData("humidite",'2023-10-24 8:55:04.320',25.0,'serre_1')
    addData("humidite",'2023-10-24 10:55:04.320',18.0,'serre_1')
    addData("humidite",'2023-10-24 12:55:04.320',22.0,'serre_1')
    addData("humidite",'2023-10-24 14:55:04.320',25.0,'serre_1')

    #serre 2
        #temperature
    addData("temperature",'2023-10-23 10:55:04.320',25.0,'serre_2')
    addData("temperature",'2023-10-23 12:55:04.320',32.0,'serre_2')
    addData("temperature",'2023-10-23 14:55:04.320',18.0,'serre_2')
    addData("temperature",'2023-10-23 16:55:04.320',21.0,'serre_2')
    addData("temperature",'2023-10-23 18:55:04.320',28.0,'serre_2')
    addData("temperature",'2023-10-23 20:55:04.320',25.0,'serre_2')
    addData("temperature",'2023-10-23 22:55:04.320',18.0,'serre_2')
    addData("temperature",'2023-10-24 0:55:04.320',22.0,'serre_2')
    addData("temperature",'2023-10-24 2:55:04.320',25.0,'serre_2')
    addData("temperature",'2023-10-24 4:55:04.320',18.0,'serre_2')
    addData("temperature",'2023-10-24 6:55:04.320',22.0,'serre_2')
    addData("temperature",'2023-10-24 8:55:04.320',25.0,'serre_2')
    addData("temperature",'2023-10-24 10:55:04.320',18.0,'serre_2')
    addData("temperature",'2023-10-24 12:55:04.320',22.0,'serre_2')
    addData("temperature",'2023-10-24 14:55:04.320',25.0,'serre_2')
        #humidite
    addData("humidite",'2023-10-23 10:55:04.320',25.0,'serre_2')
    addData("humidite",'2023-10-23 12:55:04.320',32.0,'serre_2')
    addData("humidite",'2023-10-23 14:55:04.320',18.0,'serre_2')
    addData("humidite",'2023-10-23 16:55:04.320',21.0,'serre_2')
    addData("humidite",'2023-10-23 18:55:04.320',28.0,'serre_2')
    addData("humidite",'2023-10-23 20:55:04.320',25.0,'serre_2')
    addData("humidite",'2023-10-23 22:55:04.320',18.0,'serre_2')
    addData("humidite",'2023-10-24 0:55:04.320',22.0,'serre_2')
    addData("humidite",'2023-10-24 2:55:04.320',25.0,'serre_2')
    addData("humidite",'2023-10-24 4:55:04.320',18.0,'serre_2')
    addData("humidite",'2023-10-24 6:55:04.320',22.0,'serre_2')
    addData("humidite",'2023-10-24 8:55:04.320',25.0,'serre_2')
    addData("humidite",'2023-10-24 10:55:04.320',18.0,'serre_2')
    addData("humidite",'2023-10-24 12:55:04.320',22.0,'serre_2')
    addData("humidite",'2023-10-24 14:55:04.320',25.0,'serre_2')




#affichage de toutes les données
getDataAll()

#affichage des données du capteur vent en particulier
getDataName("anemometre")

time.sleep(1)

#affichage des données entre deux dates
getDataDate('2023-10-23 22:50:00.000','2023-10-23 22:58:00.000')

#affichage des données entre deux valeurs du capteur
getDataValue("anemometre",40.0,50.0)
#clearData()