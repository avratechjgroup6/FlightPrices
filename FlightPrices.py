from datetime import datetime
import ssl
import db_procs
from flask import Flask, redirect, url_for, render_template, request, session
from instance import session_key
from data_functions import get_offers, score, price, format_offer, \
    format_date, get_airline, hash_pw, send_reset_pw_email, \
    make_stats, graph_stats
from offer import Offer
from search import Search
from user import User

db_procs.init()

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(SECRET_KEY=session_key))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('ssl/host.cert', 'ssl/host.key')


@app.route('/')
def index():
    user_id = session.get('user_id')
    session['user_id'] = user_id if user_id else 1
    if not session.get('logged_in'):
        session['user_id'] = 1
    if session['user_id'] == 1:
        return render_template("welcome_page.html")
    else:
        return redirect(url_for('homepage'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        s = Search(session['user_id'],
                   request.form.get('origin'),
                   request.form.get('destination'),
                   request.form.get('departure_date')
                   )
        currency = s.currency()
        offers = s.response
        for offer in offers:
            offer['airline'] = get_airline(offer['airline'])
            Offer(s.id, offer)  # format and insert into db
        offers = get_offers(s.id, request.form.get('exact_date'))
        offers.sort(key=price, reverse=True)  # Yes, descending.
        offers.sort(key=score, reverse=True)  # score desc, price asc
        for offer in offers:
            i = offers.index(offer)
            offers[i] = format_offer(offer, currency)
        session['offers'] = offers
        return redirect(url_for('show_offers'))
    today = datetime.today().isoformat().split('T')[0]
    return render_template("search.html", today=today)


@app.route('/show_offers')
def show_offers():
    user = db_procs.get_user(session['user_id'])
    offers = session['offers']
    if not offers:
        return render_template('no_offers.html', user=user)
    search_id = offers[0][0]
    user_search = db_procs.get_search(search_id)
    origin = user_search[2]
    destination = user_search[3]
    departure_date = format_date(user_search[4])
    return render_template('show_offers.html', user=user, offers=offers,
                           origin=origin, destination=destination,
                           departure_date=departure_date)


@app.route('/submit_choice', methods=['POST'])
def submit_choice():
    offers = session['offers']
    ichoice = int(request.form.get('ichoice'))
    choice = offers[ichoice]
    db_procs.choose_offer(choice[0], choice[4], choice[1])
    choice = choice[1:]  # discard search id
    return render_template("thank_you.html", choice=choice)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            User(name, email, password)
            session['user_id'] = db_procs.get_user_id(email)
            session['logged_in'] = True
            return redirect(url_for("homepage"))
        except ValueError as err:
            if "name" in err.args:
                return render_template("register_bad_name.html")
            if "email" in err.args:
                return render_template("register_bad_email.html")
            if "passwd" in err.args:
                return render_template("register_bad_password.html")
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            found_pw = db_procs.get_password(email)
        except:
            return render_template("required_fields.html")
        if found_pw:
            if found_pw == hash_pw(request.form.get('password')):
                session['user_id'] = db_procs.get_user_id(email)
                session['logged_in'] = True
                return redirect(url_for("homepage"))
            else:
                return render_template("login_wrong_pw.html")
        else:
            return render_template("login_no_email.html")
    return render_template("login.html")


@app.route('/homepage')
def homepage():
    try:
        user = db_procs.get_user(session['user_id'])
    except TypeError:
        session.pop('logged_in', None)
        session.pop('user_id', None)
        return redirect(url_for('index'))
    return render_template("homepage.html", user=user)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return render_template('logout.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_pw():
    if request.method == 'POST':
        email = request.form.get('email')
        if db_procs.get_user_id(email):
            code = send_reset_pw_email(email)
            db_procs.insert_code(email, code)
            return render_template('email_sent.html')
        else:
            return render_template("no_email_anon.html")
    return render_template('forgot_pw.html')


@app.route('/confirm_email', methods=['GET', 'POST'])
def confirm_email():
    if request.method == 'POST':
        user_id = session['user_id']
        our_code = db_procs.get_code(user_id).strip()
        user_code = request.form.get('user_code').strip()
        if not user_code:
            return render_template("pw_reset_fail.html")
        if user_code == our_code:
            return redirect(url_for('reset_pw'))
        else:
            return render_template("pw_reset_fail.html")
    session['user_id'] = int(request.args.get('conf'))
    return render_template('confirm_email.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_pw():
    if request.method == 'POST':
        pw = request.form.get('new_pw')
        hashed_pw = hash_pw(pw)
        db_procs.reset_pw(session['email'], hashed_pw)
        session['logged_in'] = True
        return render_template('pw_reset.html')
    session['email'] = db_procs.get_user_email(session['user_id'])
    return render_template('reset_pw.html')


@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    try:  # user must be logged in
        if not session['user_id'] > 1:
            raise KeyError
    except KeyError:
        return redirect(url_for('index'))
    if request.method == 'POST':
        params = {}
        for key, val in request.form.items():
            if val:
                params[key] = val
        stats = make_stats(params)
        graphs = graph_stats(stats, session['user_id'])
        return render_template('show_stats.html', graphs=graphs)
    return render_template('stats_search.html')


@app.route('/history')
def history():
    try:  # user must be logged in
        if not session['user_id'] > 1:
            raise KeyError
    except KeyError:
        return redirect(url_for('index'))
    user_history = db_procs.get_history(session['user_id'])
    for entry in user_history:
        entry['date'] = format_date(entry['date'])
    return render_template('show_history.html', history=user_history)

if __name__ == '__main__':
    app.run(ssl_context=context)
