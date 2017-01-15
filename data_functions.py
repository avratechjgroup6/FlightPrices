import datetime
import smtplib
import numpy as np
import matplotlib.pyplot as plot
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hashlib import sha1
from random import randint
from instance import our_mail_pw, salt
from db_procs import get_search_date, get_offered_dates, \
    get_offers as db_get_offers, get_score
from db_procs import get_user, get_stats
from flight_data import airlines, airports, cities


def json_update():
    pass  # todo: api request to update our json data


def make_id(user_id):
    timestamp = datetime.datetime.now().isoformat()\
        .replace('-', '').replace(':', '').replace('.', '')
    return "{0}-{1}".format(user_id, timestamp)


def split_time_stamp(ts):
    return ts.strip('Z').split('T')


def get_offers(search_id, exact_date):
    if exact_date:
        results = []
        requested_date = get_search_date(search_id)
        offered_dates = get_offered_dates(search_id)
        offers = db_get_offers(search_id)
        i = 0
        for offered_date in offered_dates:
            if requested_date == offered_date:
                results.append(offers[i])
            i += 1
    else:
        results = db_get_offers(search_id)
    return results


def get_airline(key):
    for airline in airlines:
        if airline["is_active"] is True:
            if airline["name"] and key.upper() == airline["name"].upper() \
                    or airline["alias"] \
                        and key.upper() == airline["alias"].upper() \
                    or airline["iata"] \
                        and key.upper() == airline["iata"].upper() \
                    or airline["icao"] \
                        and key.upper() == airline["icao"].upper() \
                    or airline["callsign"] \
                        and key.upper() == airline["callsign"].upper():
                return airline["name"]


def get_airport(key):
    for airport in airports:
        if airport["name"] and key.upper() == airport["name"].upper() \
                or airport["code"] and key.upper() == airport["code"].upper():
            return airport["name"]


def get_city(key):
    for city in cities:
        if key['code'].upper() == city['code'] \
                or key['name'].upper() == city['name'].upper() \
                or key['coordinates'].upper() == city['coordinates'].upper():
            return city['name']


def score(o):
    return get_score(o[3])


def price(o):
    return round(float(o[1]))


def format_offer(offer, currency):
    return (
            offer[0],  # search id
            format_date(offer[4]),
            format_time(offer[5]),
            get_airline(offer[2]),
            offer[3],  # flight number
            format_price(offer[1], currency)
            )


def format_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").strftime("%A, %d %B %Y")


def unformat_date(s):
    return datetime.datetime.strptime(s, "%A, %d %B %Y").strftime("%Y-%m-%d")


def format_time(s):
    return datetime.datetime.strptime(s, "%X").strftime("%I:%M%p")


def format_price(price, currency):
    return "{0} {1}".format(price, currency)


def hash_pw(s):
    return sha1(s.encode() + salt).hexdigest()


def send_reset_pw_email(email):

    user = get_user(email)
    code = '{:05}'.format(randint(1, 99999))

    msg = MIMEMultipart()
    msg['Subject'] = "FlightPrices.avratechj: Reset Password"
    msg['From'] = "avratechj.group6@gmail.com"
    msg['To'] = user['email']

    html = '''
        <html>
            <body>
                <h1>Hello {name},</h1>
                <p>
                    To reset your password, please follow the link:
                    <br><br>
                    <a
                    href="https://localhost:5000/confirm_email?conf={user_id}">
                        FlightPrices.avratechj/confirm_email
                    </a>
                    <br><br>
                    and enter the code: &nbsp;&nbsp;{code}.
                </p>
            </body>
        </html>
    '''.format(name=user['name'], user_id=user['user_id'], code=code)

    # img_data = open('test.JPG', 'rb').read()
    # image = MIMEImage(img_data, name=os.path.basename('test.JPG'))
    # msg.attach(image)

    part = MIMEText(html, 'html')
    msg.attach(part)
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login("avratechj.group6@gmail.com", our_mail_pw)
    s.sendmail("avratechj.group6@gmail.com", email, msg.as_string())
    s.quit()

    return code


def make_stats(params):
    stats = {}
    data = get_stats(params)
    for entry in data:
        for a, b in entry.items():
            a = a.title()
            if not stats.get(a):
                stats[a] = {}
            if not stats[a].get(b):
                stats[a][b] = 1
            else:
                stats[a][b] += 1
    return stats


def graph_stats(stats, user_id):
        graphs = {}
        for tbl in stats:
            plot.bar(np.arange(len(stats[tbl].keys())),
                     np.array(list(stats[tbl].values())),
                     align='center', color='green'
                     )
            plot.xticks(np.arange(len(stats[tbl])), list(stats[tbl].keys()),
                        rotation=90)
            plot.xlabel(tbl)
            plot.ylabel('Flights')
            graph_fname = r'static/images/' + tbl + str(user_id) + \
                          make_id(user_id) + r'.png'
            plot.savefig(graph_fname)
            plot.close()
            graphs[tbl] = graph_fname
        return graphs
