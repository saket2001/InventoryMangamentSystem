from flask import Flask, render_template, request, redirect, flash, session
from flaskext.mysql import MySQL
app = Flask(__name__)  # creating the Flask class object

mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = 'saket2315'
app.config["MYSQL_DATABASE_DB"] = 'ims'
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
mysql.init_app(app)

app.config['SECRET_KEY'] = 'IMS'

# global variable for using in all pages
username = ""


@app.route('/', methods=['GET', 'POST'])  # decorator defines the
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global username
        username = request.form['username']
        password = request.form['password']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM `user` WHERE `username` = '" +
                    username + "' and `password` = '" + password + "'")
        data = cur.fetchone()
        if data is None:
            flash("Error: User not found or something went wrong!! Try again")
        else:
            if data[1] == username and data[2] == password:
                flash("Logged in successfull !")
                return render_template('dashboard.html', username=username)
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    con = mysql.connect()
    cur = con.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pass_word = request.form['pass_word']
        name = request.form['name']
        birth_date = request.form['birth_date']
        contact_no = request.form['contact_no']
        cur.execute("SELECT * from `user` WHERE `username` = '" +
                    username + "' and `name` = '" + name + "'")
        signup_data = cur.fetchone()
        # form validation
        if len(password) < 7 or len(password) > 30:
            flash('password must have length of 8 and and max of 30',
                  category='error')
        else:
            if not any(char.isdigit() for char in password):
                flash('Password should have at least one numerical',
                      category='error')
            else:
                if not any(char.isupper() for char in password):
                    flash(
                        'Password should have at least one uppercase letter', category='error')
                else:
                    if not any(char.islower() for char in password):
                        flash(
                            'Password should have at least one lowercase letter', category='error')
                    else:
                        if len(contact_no) < 10:
                            flash('Give proper contact no', category='error')
                        else:
                            if password != pass_word:
                                flash('Password doesn\'t match re-entered password',
                                      category='error')
                            else:
                                if password == pass_word:
                                    cur.execute("INSERT INTO `user`(`username`,`password`,`name`,`birth_date`,`contact_no`) VALUES (%s,"
                                                "%s,%s,%s,%s)", (username, password, name, birth_date, contact_no))
                                    con.commit()
                                    return redirect('login')
                                else:
                                    flash('account created',
                                          category='success')
    return render_template("signup.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", username=username)


@app.route('/dashboard/EditInventory')
def EditInventory():
    return render_template("EditInventory.html", username=username)


# @app.route('/dashboard/ViewInventory')
# def viewInventory():
#     return render_template("viewInventory.html")

@app.route('/dashboard/newInvoice')
def newInvoice():
    return render_template("newInvoice.html", username=username)


@app.route('/dashboard/newsuppliers')
def suppliers():
    return render_template("suppliers.html", username=username)


app.run(debug=True)
