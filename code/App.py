from flask import Flask, render_template, request, redirect, flash, session, url_for
import uuid
from flaskext.mysql import MySQL
import datetime
app = Flask(__name__)  # creating the Flask class object

mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = 'saket2315'
app.config["MYSQL_DATABASE_DB"] = 'ims2'
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
mysql.init_app(app)

app.config['SECRET_KEY'] = 'IMS'

###################################
# global variables
BillProducts = []
customer_name = ""
BillID = ""


# variable for date
x = datetime.datetime.now()
displayDate = x.strftime("%x")

###################################
# helper functions


def calcTotalBill():
    sum = 0
    total_amount = 0
    for x in BillProducts:
        cur = x[4]
        sum = sum+cur
        total_amount = sum

    return total_amount


def formatNumber(num):
    return ('{:0,d}'.format(num))
# to update stocks on invoice


def UpdateStockOnInvoice(p_id, p_quantity, opt):
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        userid = username
        # getting the old stock
        cur.execute(
            "SELECT `product_instock`,`product_maxlimit` FROM `product` WHERE `userid` = '" + userid + "' and `productid`= '" + p_id + "'")
        # calc the new stock
        currentStock = cur.fetchone()

        # for adding stock on invoice
        if opt == "invoiceadd":
            newStock = int(currentStock[0])+int(p_quantity)
        # for adding stock
        if opt == "add":
            newStock = int(currentStock[0])+int(p_quantity)
        # for deleteing stock
        if opt == "sub":
            newStock = int(currentStock[0])-int(p_quantity)

        # this checks if updated stock request is greater then max limit or not
        if newStock > currentStock[1]:
            flash("You cannot add product stock over product max limit")
        # this checks if after substraction the stock is in negative
        if newStock < 0:
            flash("Product Stock are less for fulfilling this request")
            return 0

        # add the new stock
        cur.execute("UPDATE `product` SET `product_instock`= '" + str(newStock) +
                    "' WHERE `userid`= '" + userid + "' and `productid`= '" + p_id + "'")
        flash("NEW !! Inventory updated 1 sec ago")
        conn.commit()
    else:
        return redirect(url_for("login"))


# for counting details in inventory

def CountDetailsOfInventory(option):
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        userid = username
        if option == 1:
            cur.execute(
                "SELECT Count(productid) FROM `product` WHERE `userid` = '" + userid + "'")
        if option == 2:
            cur.execute(
                "SELECT Count(supplier_id) FROM `supplier` WHERE `userid` = '" + userid + "'")
        if option == 3:
            cur.execute(
                "SELECT Count(invoice_id) FROM `invoice` WHERE `userid` = '" + userid + "'")
        total_product = cur.fetchone()
        return total_product[0]
    else:
        return redirect(url_for("dashboard"))

# function to check stocks


def checkStocks():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        userid = username
        # this gets all the products from the inventory
        cur.execute(
            "SELECT `product_name`,`productid`,`product_maxlimit`,`product_minlimit`,`product_instock` FROM `product` WHERE `userid` = '" + userid + "'")
        inventory = cur.fetchall()
        print(inventory)
        # now checking each product for stocks
        for product in inventory:
            # print(product[3])
            if product[4] == 0:
                flash("Product {} with id {} are empty in inventory".format(
                    product[0], product[1]))
            if product[4] <= product[3]:
                flash("Product {} with id {} is close to being empty".format(
                    product[0], product[1]))
    else:
        return redirect(url_for("dashboard"))

#


def myprofile(option):
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        userid = username
        if option == 1:
            cur.execute(
                "SELECT `name` FROM `user` WHERE `username` = '" + userid + "'")
        if option == 2:
            cur.execute(
                "SELECT `dob` FROM `user` WHERE `username` = '" + userid + "'")
        if option == 3:
            cur.execute(
                "SELECT `contact_no` FROM `user` WHERE `username` = '" + userid + "'")
        Profile_data = cur.fetchone()
        return Profile_data[0]
    else:
        return redirect(url_for("dashboard"))

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
                return redirect(url_for('dashboard'))
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
        # calling helper functions
        total_product = CountDetailsOfInventory(1)
        total_suppliers = CountDetailsOfInventory(2)
        total_invoices = CountDetailsOfInventory(3)
        # checking if stocks are empty or close to minlimit
        checkStocks()

        return render_template("dashboard.html", username=username, date=displayDate, total_product=total_product, total_suppliers=total_suppliers, total_invoices=total_invoices)
    else:
        return redirect("login")


@app.route('/dashboard/myprofile')
def profile():
    conn = mysql.connect()
    cur = conn.cursor()
    if 'username' in session:
        username = session["username"]
        Profile_name = myprofile(1)
        Profile_dob = myprofile(2)
        Profile_contactno = myprofile(3)
        return render_template("profile.html", username=username, date=displayDate, name=Profile_name, dob=Profile_dob, contact_no=Profile_contactno)
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


@app.route('/dashboard/billing')
def billing():
    if 'username' in session:
        username = session["username"]
        return render_template("billing.html", username=username, date=displayDate)
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
            userid = username
            product_id = request.form['p-id']
            product_quantity = request.form['p-quantity']
            UpdateStockOnInvoice(product_id, product_quantity, "add")
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


@app.route('/updateMaxLimit', methods=["GET", "POST"])
def updateProductLimit():
    if 'username' in session:
        username = session["username"]
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                userid = username
                p_id = request.form['p-id']
                p_maxlimit = request.form['p-maxlimit']
                # adding to stocks
                cur.execute("UPDATE `product` SET `product_maxlimit`= '" + p_maxlimit + "' WHERE `userid`= '" +
                            userid + "' and `productid`= '" + p_id + "'")
                conn.commit()
                flash("Maximum limit of product id {} updated successfully".format(
                    p_id))
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
                                     * int(product_quantity))

                # adding data to db
                cur.execute("INSERT INTO `invoice` (`supplier_id`,`supplier_name`,`supplier_type`,`userid`,`invoice_date`,`product_id`,`product_name`,`product_quantity`,`product_prices`,`total_amount`) VALUES (%s,"
                            "%s,%s,%s,%s,%s,%s,%s,%s,%s)", (supplier_id, supplier_name, supplier_type, userid, invoiceDate, product_id, product_name, product_quantity, product_price, totalAmtOfInvoice))
                conn.commit()
                flash("Your order worth {} Rs Has been placed.".format(
                    totalAmtOfInvoice))
                UpdateStockOnInvoice(
                    product_id, product_quantity, "invoiceadd")
            except:
                flash("Something went wrong ! Try again")
                conn.close()
            return redirect(url_for('newInvoice'))
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

# function to do the following
# 1.Get data one by one from form
# 2.print that data one by one in the bill
# 3.calculate total of bill
# 4.print the whole bill
# 5.Update the stock of products selling


@app.route('/dashboard/Createbill', methods=["GET", "POST"])
def GetBilldetail():
    if 'username' in session:
        username = session["username"]
        # all the data from the db will be in tuple in tuple form
        conn = mysql.connect()
        cur = conn.cursor()
        try:
            # get data
            userid = username
            global customer_name
            c_name = request.form['c_name']
            c_contact = request.form['c_contact']
            bill_date = displayDate
            p_id = request.form['p-id']
            p_name = request.form['p-name']
            p_quantity = request.form['p-quantity']
            p_price = request.form['p-price']
            totalOfProducts = int(p_price)*int(p_quantity)

            # this deletes the stocks which are being sold

            result = UpdateStockOnInvoice(p_id, p_quantity, "sub")
            if result != 0:
                # this prints to bill
                curProduct = [p_id, p_name, p_quantity,
                              p_price, totalOfProducts, c_name, c_contact]
                global BillProducts
                BillProducts.append(curProduct)

        except:
            flash("Error")
        return render_template("billing.html", username=username, date=displayDate, bill_detail=BillProducts)
    else:
        return redirect("login")


@app.route("/Showbill", methods=["GET"])
def showBill():
    if 'username' in session:
        username = session["username"]
        # this calculates the total bill amount
        totalBill = calcTotalBill()
        # tax
        to_pay = 0
        if totalBill <= 1000:
            tax = 20
            to_pay = totalBill+tax
        elif totalBill >= 1000 and totalBill <= 10000:
            tax = 62
            to_pay = totalBill+tax
        elif totalBill > 10000 and totalBill <= 50000:
            tax = 100
            to_pay = totalBill+tax
        else:
            tax = 135
            to_pay = totalBill+tax

        _totalBill = formatNumber(totalBill)
        _to_pay = formatNumber(to_pay)

        # Stores the selling record to db
        c_name = BillProducts[0][5]
        c_contact = BillProducts[0][6]

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO `billing_record`(`userid`,`bill_id`,`customer_name`,`bill_date`,`bill_total`,`customer_contact`) VALUES (%s,"
                    "%s,%s,%s,%s,%s)", (username, BillID, c_name, displayDate, to_pay, c_contact))
        conn.commit()
        #
        return render_template("bill.html", username=username, date=displayDate, bill_detail=BillProducts, total_amount=_totalBill, customer_name=c_name, customer_contact=c_contact, billID=BillID, tax=tax, to_pay=_to_pay)
    else:
        return redirect("login")


@app.route("/ClearBillArray")
def clearBill():
    if 'username' in session:
        username = session["username"]
        # genrates a unique bill id
        myuuid = uuid.uuid4()
        strUid = str(myuuid)
        global BillID
        BillID = strUid[0:7]
        # clear the bill product list
        global BillProducts
        BillProducts.clear()
        return render_template("billing.html", username=username, date=displayDate, bill_detail=BillProducts, billID=BillID)
    else:
        return redirect("login")


@app.route('/searchBill', methods=["GET", "POST"])
def searchBill():
    if 'username' in session:
        username = session["username"]
        conn = mysql.connect()
        cur = conn.cursor()
        # get data
        try:
            userid = username
            b_id = request.form['b-id']
            # b_id = '1ba53a7'
            cur.execute("SELECT * FROM `billing_record` WHERE `userid`= '" +
                        userid + "' and `bill_id`='" + b_id+"'")
            billlist = cur.fetchall()
            print(billlist)
        except:
            flash("Error getting your bill")
        return render_template("billing.html", username=username, date=displayDate, bills=billlist)
    else:
        return redirect("login")


@app.route('/updatepassword', methods=['POST'])
def Updatepassword():
    if 'username' in session:
        username = session["username"]
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == 'POST':
            try:
                userid = username
                Old_password = request.form["old_password"]
                New_password = request.form["new_password"]
                cur.execute(
                    "SELECT `password` FROM `user` WHERE `username` = '" + userid + "'")
                user_password = cur.fetchone()
                if Old_password != user_password[0]:
                    flash("Old Password of user {} does not match".format(userid))
                else:
                    cur.execute("UPDATE `user` SET `password`= '" +
                                New_password + "' WHERE `username`= '" + userid + "'")
                    conn.commit()
                    flash("Password of user {} updated successfully".format(userid))
            except:
                flash("Error while getting your password")
        return redirect(url_for("login"))
    else:
        return redirect("login")


@app.route("/deleteuseraccount", methods=["GET", "POST"])
def deleteuser():
    if 'username' in session:
        username = session["username"]
        # making connection
        conn = mysql.connect()
        cur = conn.cursor()
        if request.method == "POST":
            try:
                userid = username
                password = request.form["password"]
                # executing query
                cur.execute(
                    "SELECT `password` FROM `user` WHERE `username` = '" + userid + "'")
                User_password = cur.fetchone()
                if password != User_password[0]:
                    flash("Please give correct Password")
                else:
                    cur.execute(
                        "DELETE FROM `user` WHERE `username` = '" + userid + "'")
                    conn.commit()
                    flash("Account of user {}, has been deleted".format(userid))
            except:
                flash("Error while clearing user")
        return redirect(url_for("login"))
    else:
        return redirect("login")


#############################
app.run(debug=True)
