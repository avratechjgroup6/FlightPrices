import sqlite3
from validation import check_name, check_email


def init():
    con = sqlite3.connect("FlightPrices.db")
    c = con.cursor()

    c.execute('''
      CREATE TABLE IF NOT EXISTS searches(
        id CHAR,
        user INTEGER,
        origin CHAR,
        destination CHAR,
        date CHAR
      )
    ''')

    c.execute('''
      CREATE TABLE IF NOT EXISTS offers(
        id CHAR,
        price CHAR,
        airline CHAR,
        flight_no CHAR,
        date CHAR,
        time CHAR,
        chosen INTEGER
      )
    ''')

    c.execute('''
      CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        name CHAR,
        email CHAR,
        password CHAR,
        code CHAR
      )
    ''')

    c.execute('''
      INSERT INTO users(name,email,password)
      SELECT "anon","anon","anon"
      WHERE NOT exists (SELECT * FROM users WHERE email="anon")
    ''')

    con.commit()
    con.close()


def insert_search(search_id, user, origin, destination, date):
        con = sqlite3.connect('FlightPrices.db')
        c = con.cursor()
        c.execute('''
                  INSERT INTO searches VALUES (?,?,?,?,?)
                  ''', (search_id, user, origin, destination, date,)
                  )
        con.commit()
        con.close()


def insert_offer(search_id, user_id, airline, flight_no,
                 date, time):
        con = sqlite3.connect('FlightPrices.db')
        c = con.cursor()
        c.execute('''
                  INSERT INTO offers VALUES (?,?,?,?,?,?,?)
                  ''', (search_id, user_id, airline, flight_no, date, time, 0,)
                  )
        con.commit()
        con.close()


def insert_user(name, email, password):
        con = sqlite3.connect('FlightPrices.db')
        c = con.cursor()
        c.execute('''
                  INSERT INTO users(name,email,password) VALUES (?,?,?)
                  ''', (name, email, password)
                  )
        con.commit()
        con.close()


def get_user(key):
    con = sqlite3.connect("FlightPrices.db")
    c = con.cursor()
    if check_name(key):
        c.execute('''SELECT * from users WHERE name==?''', (key,))
    elif check_email(key):
        c.execute('''SELECT * from users WHERE email==?''', (key,))
    elif type(key) is int:
        c.execute('''SELECT * from users WHERE id==?''', (key,))
    user = c.fetchone()
    con.close()
    user = {'user_id': user[0], 'name': user[1], 'email': user[2]}
    return user


def get_user_id(key):
    con = sqlite3.connect("FlightPrices.db")
    c = con.cursor()
    if check_name(key):
        c.execute('''SELECT id from users WHERE name==?''', (key,))
    elif check_email(key):
        c.execute('''SELECT id from users WHERE email==?''', (key,))
    user_id = c.fetchone()[0]
    con.close()
    return int(user_id)


def get_user_email(key):
    con = sqlite3.connect("FlightPrices.db")
    con.row_factory = sqlite3.Row
    c = con.cursor()
    if check_name(key):
        c.execute('''SELECT email from users WHERE name==?''', (key,))
    elif type(key) is int:
        c.execute('''SELECT email from users WHERE id==?''', (key,))
    email = c.fetchone()[0]
    con.close()
    return email


def get_user_name(user_id):  # todo: uid or email
    con = sqlite3.connect("FlightPrices.db")
    c = con.cursor()
    c.execute('''SELECT name from users WHERE id==?''', (user_id,))
    uname = c.fetchone()[0]
    con.close()
    return uname


def get_password(email):
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''SELECT password FROM users WHERE email=?''', (email,))
    pw = c.fetchone()[0]
    con.close()
    return pw


def get_search(search_id):
    con = sqlite3.connect("FlightPrices.db")
    c = con.cursor()
    c.execute('''SELECT * FROM searches WHERE id=?''', (search_id,))
    search = c.fetchall()[0]
    con.close()
    return search


def get_offers(search_id):
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''SELECT * FROM offers WHERE id==?''', (search_id,))
    offers = c.fetchall()
    con.close()
    return offers


def get_search_date(search_id):
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''SELECT date FROM searches WHERE id==?''', (search_id,))
    date = c.fetchall()[0][0]
    con.close()
    return date


def get_offered_dates(search_id):
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''SELECT date FROM offers WHERE id==?''', (search_id,))
    date = c.fetchall()[0][0]
    con.close()
    return date


def get_score(flight_no):
    score = 0
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''SELECT chosen FROM offers WHERE flight_no==?''', (flight_no,))
    for point in c.fetchall():
        score += int(point[0])
    con.close()
    return score


def choose_offer(search_id, flight_no, date):
    from datetime import datetime
    date = datetime.strptime(date, "%A, %d %B %Y").strftime("%Y-%m-%d")
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''
              UPDATE offers
              SET chosen=1
              WHERE id=?
              AND flight_no=?
              AND date=?
              ''', (search_id, flight_no, date,)
              )
    con.commit()
    con.close()


def insert_code(email, code):
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''UPDATE users SET code=? WHERE email=?''', (code, email,))
    con.commit()
    con.close()


def get_code(user_id):
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''SELECT code FROM users WHERE id=?''', (user_id,))
    code = c.fetchone()[0]
    con.close()
    return code


def reset_pw(email, pw):
    con = sqlite3.connect('FlightPrices.db')
    c = con.cursor()
    c.execute('''UPDATE users SET password=? WHERE email=?''', (pw, email,))
    # Remove the code
    c.execute('''UPDATE users SET code=NULL WHERE email=?''', (email,))
    con.commit()
    con.close()


def get_stats(params):
    con = sqlite3.connect('FlightPrices.db')
    con.row_factory = sqlite3.Row
    c = con.cursor()

    sql = '''SELECT DISTINCT searches.origin, searches.destination,
                    offers.price, offers.date, offers.airline
             FROM offers
             JOIN searches
             ON offers.id = searches.id
             WHERE 1=1'''
    if 'price' in params:
        sql += " AND price=:price"
    if 'airline' in params:
        sql += " AND airline=:airline"
    if 'date' in params:
        sql += " AND date=:date"
    if 'origin' in params:
        sql += " AND origin=:origin"
    if 'destination' in params:
        sql += " AND destination=:destination"

    c.execute(sql, params)

    stats = []
    for entry in c.fetchall():
        tmp = {}
        for key in entry.keys():
            tmp[key] = entry[key]
        stats.append(tmp)

    con.close()

    return stats


def get_history(user_id):
    con = sqlite3.connect('FlightPrices.db')
    con.row_factory = sqlite3.Row
    c = con.cursor()

    history = []

    c.execute('''
              SELECT origin,destination,date
              FROM searches
              WHERE user=?
              ''', (user_id,)
              )
    for entry in c.fetchall():
        tmp = {'type': 'search'}
        for key in entry.keys():
            tmp[key] = entry[key]
        history.append(tmp)

    c.execute('''
              SELECT offers.price, offers.flight_no,
                  offers.airline, offers.date, offers.time,
                  searches.origin, searches.destination
              FROM offers
              JOIN searches ON offers.id=searches.id
              WHERE searches.user=?
              AND offers.chosen=1
              ''', (user_id,)
              )
    for entry in c.fetchall():
        tmp = {'type': 'offer'}
        for key in entry.keys():
            tmp[key] = entry[key]
        history.append(tmp)

    return history
