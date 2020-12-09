from flask import Flask
from flask import request
from flask import g
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import io
from flask import send_file

from idea_datalayer import IdeaData

app = Flask(__name__)
app.secret_key = 'very secret string'

data = None
update = False
show = True
# list_fig_1 = [10,2,3,40]
# list_fig_2 = [1,20,30,4]

@app.teardown_appcontext
def close_connection(exception):
    data.close_connection()


"""
Denne funktion sørger for at pakke den template, der skal vises,
ind i nogle standard-ting, f.eks. loginstatus.

my_render bør kaldes i stedet for at kalde render_template direkte.
"""
def my_render(template, **kwargs):
    login_status = get_login_status()
    if login_status:
        return render_template(template, loggedin=login_status, user = session['currentuser'], **kwargs)
    else:
        return render_template(template, loggedin=login_status, user = '', **kwargs)

def get_login_status():
    return 'currentuser' in session

def get_user_id():
    if get_login_status():
        return session['currentuser']
    else:
        return -1

@app.route("/")
@app.route("/home")
def home():
    return my_render('home.html')

@app.route("/profil")
def profil():
    return redirect("/vistracker")

@app.route("/new_tracker")
def new_tracker():
    return my_render("/new_tracker.html")


@app.route("/nyide", methods=['POST'])
def nyide():
    navn = request.form['navn']
    type = request.form['input']
    if type == 'tal':
        type_out = 0
    elif type == 'tekst':
        type_out = 1
    elif type == 'emoji':
        type_out = 2
    view = request.form['view']
    if view == 'graf':
        view_out = 0
    elif view == 'søjle':
        view_out = 1
    elif view == 'cirkel':
        view_out = 2
    userid = get_user_id()
    data.register_vars(userid, navn, type_out, view_out)

    return redirect("/profil")


@app.route("/vistracker", methods=['GET', 'POST'])
def vis_tracker():

    if 'currentuser' in session:
        if 'id' in request.args:
            id = request.args['id']
            data.get_graf_list(id)
            fig()
            if request.method == 'POST':
                a_input = request.form['input']
                a_id = request.args['id']
                print(a_input)
                print(a_id)
                data.add_track_data(a_input, a_id)
                graf = data.get_graf_list(a_id)


            tracker = data.get_tracker_list(session['currentuser'], trackerid = request.args['id'])
            show = False
            var = "text"
            # list_fig_1 = []
            # list_fig_2 = []
            # for i in data.get_graf_list(1):
            #     data.list_fig_1.append(i[0])
            #     data.list_fig_2.append(i[1])
        else:
            tracker = data.get_tracker_list(session['currentuser'])
            show = True
            var = False
            update = False
        if 'input' in request.args:
            print("input: {}".format(input))

    else:
        tracker = []
    return my_render("vis.html", trackers = tracker, show_but= show, type_var= var)

@app.route("/update_table", methods=['GET'])
def update_table():
    input = request.form['input']
    print(input)
    return redirect("/vistracker")

@app.route("/register")
def register():
    return my_render('register.html', success= True, complete = True)

@app.route("/login")
def login():
    return my_render('login.html', success = True)

@app.route("/logout")
def logout():
    session.pop('currentuser', None)
    return my_render('home.html')


@app.route("/about")
def about():
    return my_render('about.html', title='Om idéhuset')

@app.route("/contact")
def contact():
    return my_render('contact.html', title='Kontakt')

def login_success(user, pw):
    return data.login_success(user,pw)

def register_success(user, pw, email):
    return data.register_user(user, pw, email)

@app.route('/register_user', methods=['POST'])
def register_user():
    pw = request.form['password']
    user = request.form['username']
    email = request.form['email']

    if register_success(user, pw, email):
        #Create user object, store in session
        session['currentuser'] = data.get_user_id(user)
        return my_render('home.html')
    else:
        session.pop('currentuser', None)
        if len(pw) == 0 or len(user) == 0:
            return my_render('register.html', success = False, complete = False)
        else:
            return my_render('register.html', success = False, complete = True)


@app.route('/login_user', methods=['POST'])
def login_user():
    pw = request.form['password']
    user = request.form['username']

    if login_success(user, pw):
        #Create user object, store in session.
        session['currentuser'] = data.get_user_id(user)
        return my_render('home.html')
    else:
        session.pop('currentuser', None)
        return my_render('login.html', success = False)

@app.route('/fig')
def fig():
    plt.title("palle1234_er_død")
    x_list = []
    y_list = []
    for i in data.graf_list:
        x_list.append(i['timestamp'])
        y_list.append(i['value'])
    print("_____")
    print(x_list)
    print(y_list)
    plt.plot([1,2,3,4], [1,2,3,4])
    plt.show()
    img = io.BytesIO()
    plt.savefig(img)
    img.seek(0)
    print("_____opretter fig______")
    return send_file(img, mimetype='image/png')


if __name__ == "__main__":
    with app.app_context():
        data = IdeaData()

    app.run(debug=True)
