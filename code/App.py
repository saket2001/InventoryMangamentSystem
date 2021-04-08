from flask import Flask, render_template, request, redirect, flash, session
from flaskext.mysql import MySQL
import datetime
app = Flask(__name__)  # creating the Flask class object

mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = 'saket2315'
app.config["MYSQL_DATABASE_DB"] = 'ims'
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
mysql.init_app(app)

app.config['SECRET_KEY'] = 'IMS'

###################################
# variables
username = ""

# variable for date
x = datetime.datetime.now()
displayDate = x.strftime("%x")

###################################
# functions


# to calc extra charges


def CalcAndAddExtraCharges(price):
    if price >= 5000 and price <= 30000:
        return (price+1500)
    if price > 30000 and price <= 80000:
        return (price+4000)
    else:
        return (price+6000)
# to calc total amount


def CalcAmt(price, quantity):
    sum = 0
    sum = price*quantity
    total = CalcAndAddExtraCharges(sum)
    return total


# print(CalcAmt(100000, 10))
###################################


# app functions


@app.route('/', methods=['GET', 'POST'])  # decorator defines the
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        password = request.form['password']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM `user` WHERE `username` = '" +
                    username + "' and `password` = '" + password + "'")
        data = cur.fetchone()
        if data is None:
            flash("Error: User not found or something went wrong!! Try again")
        else:
            if data[0] == username and data[1] == password:
                flash("You logged in successfully ")
                return render_template('dashboard.html', username=username, date=displayDate)
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
                                    cur.execute("INSERT INTO `user`(`username`,`password`,`name`,`dob`,`contact_no`) VALUES (%s,"
                                                "%s,%s,%s,%s)", (username, password, name, birth_date, contact_no))
                                    con.commit()
                                    return redirect('login')
                                else:
                                    flash('account created',
                                          category='success')
    return render_template("signup.html")


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session["username"]
        return render_template("dashboard.html", username=username, date=displayDate)
    else:
        return redirect("login")


@app.route('/dashboard/EditInventory', methods=["GET", "POST"])
def EditInventory():
    if 'username' in session:
        username = session["username"]
        return render_template("EditInventory.html", username=username, date=displayDate)
    else:
        return redirect("login")


@app.route('/dashboard/viewInventory', methods=["GET"])
def viewInventory():
    if 'username' in session:
        username = session["username"]
        # all the data from the db will be in tuple in tuple form
        conn = mysql.connect()
        cur = conn.cursor()
        try:
            userid = username
            cur.execute(
                "SELECT * FROM `product` WHERE `userid` = '" + userid + "'")
            inventory = cur.fetchall()
        except:
            flash("Error while getting your inventory")
        return render_template("viewInventory.html", username=username, table=inventory, date=displayDate)
    else:
        return redirect("login")


@app.route('/dashboard/newInvoice')
def newInvoice():
    if 'username' in session:
        username = session["username"]
        return render_template("newInvoice.html", username=username, date=displayDate)
    else:
        return redirect("login")


@app.route('/dashboard/newsuppliers', methods=["GET", "POST"])
def suppliers():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                # getting form data
                userid = username
                supplier_id = request.form['s-id']
                supplier_name = request.form['s-name']
                supplier_type = request.form['s-type']
                supplier_contactno = request.form['s-contactno']
                # executing query
                # adding product details to product
                cur.execute("INSERT INTO `supplier` (`userid`,`supplier_id`,`supplier_name`,`supplier_type`,`supplier_contactno`) VALUES (%s,"
                            "%s,%s,%s,%s)", (userid, supplier_id, supplier_name, supplier_type, supplier_contactno))
                conn.commit()
                flash("Supplier added successfully")
            except:
                flash("Error while adding Supplier")
        return render_template("suppliers.html", username=username, date=displayDate)
    else:
        return redirect("login")


@app.route('/dashboard/viewSuppliers', methods=["GET"])
def viewSuppliers():
    if 'username' in session:
        username = session["username"]
        # all the data from the db will be in tuple in tuple form
        conn = mysql.connect()
        cur = conn.cursor()
        try:
            userid = username
            cur.execute(
                "SELECT * FROM `supplier` WHERE `userid` = '" + userid + "'")
            list = cur.fetchall()
        except:
            flash("Error while getting your suppliers list")
        return render_template("suppliers.html", username=username, table=list, date=displayDate)
    else:
        return redirect("login")


@app.route('/deleteSupplier', methods=["GET", "POST"])
def deleteSupplier():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                # getting form data
                userid = username
                supplier_id = request.form['s-id']
                # executing query
                cur.execute("DELETE FROM `supplier` WHERE `userid`= '" +
                            userid + "' and `supplier_id`='" + supplier_id+"'")
                conn.commit()
                flash("Supplier No {} Deleted successfully".format(supplier_id))
            except:
                flash("Error while deleting Supplier")
        return render_template("suppliers.html", username=username, date=displayDate)
    else:
        return redirect("login")


@app.route('/helppage')
def gotoHelpPage():
    if 'username' in session:
        username = session["username"]
        return render_template("Help.html")
    else:
        return redirect("login")


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    flash("You logged out successfully")
    return redirect("login")

# helper functions
# method for adding products detail to inventory


@app.route('/addToInventorylist', methods=["GET", "POST"])
def addToInventorylist():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                # getting form data
                userid = username
                supplier_id = request.form['s-id']
                product_id = request.form['p-id']
                product_name = request.form['p-name']
                product_category = request.form['p-category']
                product_instock = request.form['p-instock']
                product_price = request.form['p-price']
                product_maxlimit = request.form['p-maxlimit']
                product_minlimit = request.form['p-minlimit']
                # executing query
                # adding product details to product
                cur.execute("INSERT INTO `product`(`userid`,`productid`,`product_name`, `product_category`,`product_price`,`product_maxlimit`,`product_minlimit`,    `product_instock`,`supplier_id`) VALUES (%s,"
                            "%s,%s,%s,%s,%s,%s,%s,%s)", (userid, product_id, product_name, product_category, product_price, product_maxlimit, product_minlimit, product_instock, supplier_id))
                conn.commit()
                flash("Product added successfully")
            except:
                flash("Error while adding product")
            return render_template("EditInventory.html", username=username, date=displayDate)
    else:
        return redirect("login")


# update specific product stock
@app.route('/updateStock', methods=["POST"])
def updateStock():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                userid = username
                product_id = request.form['p-id']
                product_quantity = request.form['p-quantity']
                # getting the old stock
                cur.execute(
                    "SELECT `product_instock`,`product_maxlimit` FROM `product` WHERE `userid` = '" + userid + "' and `productid`= '" + product_id + "'")
                # calc the new stock
                currentStock = cur.fetchone()
                newStock = int(currentStock[0])+int(product_quantity)
                if newStock > currentStock[1]:
                    flash("You cannot add product stock over product max limit")
                else:
                    # add the new stock
                    cur.execute("UPDATE `product` SET `product_instock`= '" + str(newStock) +
                                "' WHERE `userid`= '" + userid + "' and `productid`= '" + product_id + "'")
                    conn.commit()
                    flash(
                        "Stock of product id {} updated successfully".format(product_id))
            except:
                flash("Error while updating !! Try again")
            return render_template("EditInventory.html", username=username, date=displayDate)
    else:
        return redirect("login")


@app.route('/updateStockproductToMax', methods=["GET", "POST"])
def updateProductToMax():
    if 'username' in session:
        username = session["username"]
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                userid = username
                product_id = request.form['p-id']
                # adding to stocks
                cur.execute("UPDATE `product` SET `product_instock`= `product_maxlimit` WHERE `userid`= '" +
                            userid + "' and `productid`= '" + product_id + "'")
                conn.commit()
                flash("Stock of product id {} updated to maximum product limit successfully".format(
                    product_id))
            except:
                flash("Error while updating !! Try again")
        return render_template("EditInventory.html", username=username, date=displayDate)
    else:
        return redirect("login")


# update all product stocks to max limit
@app.route('/updateallStock', methods=["POST"])
def updateallStock():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                userid = username
                # executing query
                cur.execute("UPDATE `product`SET `product_instock`= `product_maxlimit` WHERE `userid`= '" +
                            userid + "'")
                conn.commit()
                flash(
                    "Stock of all products in your inventory updated to maximum product limit successfully")
            except:
                flash("Error while updating !! Try again")
        return render_template("EditInventory.html", username=username, date=displayDate)
    else:
        return redirect("login")

# to delete a specific product


@app.route('/deleteProduct', methods=["GET", "POST"])
def deleteProduct():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                # getting form data
                userid = username
                product_id = request.form['p-id']
                # executing query
                cur.execute("DELETE FROM `product` WHERE `userid`= '" +
                            userid + "' and `productid`='" + product_id+"'")
                conn.commit()
                print("deleted product")
                flash("Product {} Deleted successfully".format(product_id))
            except:
                flash("Error while deleting product")
        return render_template("EditInventory.html", username=username, date=displayDate)
    else:
        return redirect("login")

# to delete all products


@app.route('/clearAllProducts', methods=["GET", "POST"])
def clearInventory():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                userid = username
                # executing query
                cur.execute("DELETE FROM `product` WHERE `userid`= '" +
                            userid + "'")
                conn.commit()
                flash("Inventory of{} cleared successfully".format(userid))
            except:
                flash("Error while clearing inventory")
        return render_template("EditInventory.html", username=username, date=displayDate)
    else:
        return redirect("login")


# invoice section


@app.route('/CreateNewInvoice', methods=["POST", "GET"])
def CreateNewInvoice():
    if 'username' in session:
        username = session["username"]
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                # getting all form data
                userid = username
                invoiceDate = str(displayDate)
                supplier_id = request.form["s-id"]
                supplier_name = request.form["s-name"]
                supplier_type = request.form["s-type"]
                product_id = request.form["p-id"]
                product_name = request.form["p-name"]
                product_quantity = request.form["p-quantity"]
                product_price = request.form["p-price"]

                # calc total amount
                totalAmtOfInvoice = (float(product_price)
                                     * int(product_quantity))+2000

                # adding data to db
                cur.execute("INSERT INTO `invoice` (`supplier_id`,`supplier_name`,`supplier_type`,`userid`,`invoice_date`,`product_id`,`product_name`,`product_quantity`,`product_prices`,`total_amount`) VALUES (%s,"
                            "%s,%s,%s,%s,%s,%s,%s,%s,%s)", (supplier_id, supplier_name, supplier_type, userid, invoiceDate, product_id, product_name, product_quantity, product_price, totalAmtOfInvoice))
                conn.commit()
                conn.close()
                flash("Your order worth {} Rs Has been placed.".format(
                    totalAmtOfInvoice))
            except:
                flash("Something went wrong ! Try again")
                conn.close()
            return render_template("newInvoice.html", username=username, date=displayDate)
    else:
        return redirect("login")


@app.route('/dashboard/viewInvoices', methods=["GET"])
def viewInvoices():
    if 'username' in session:
        username = session["username"]
        # all the data from the db will be in tuple in tuple form
        conn = mysql.connect()
        cur = conn.cursor()
        try:
            userid = username
            cur.execute(
                "SELECT * FROM `invoice` WHERE `userid` = '" + userid + "'")
            list = cur.fetchall()
        except:
            flash("Error while getting your suppliers list")
        return render_template("newInvoice.html", username=username, table=list, date=displayDate)
    else:
        return redirect("login")


#############################
app.run(debug=True)
