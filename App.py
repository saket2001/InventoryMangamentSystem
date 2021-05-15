from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_mail import Mail, Message
import uuid
from flaskext.mysql import MySQL
import base64
import datetime
# import mysql.connector
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # creating the Flask class object
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:saket2315@localhost/ims2"
# conn = mysql.connector.connect(
#     host="localhost", user="root", password="", database="ims2")

# sql configuration
mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = 'saket2315'
app.config["MYSQL_DATABASE_DB"] = 'ims2'
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
mysql.init_app(app)

# db connection active
conn = mysql.connect()
cur = conn.cursor()

# mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'inventorymanagement777@gmail.com'
app.config['MAIL_PASSWORD'] = 'Inventory@777'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
# flash config
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
# for password protection


def decrpytpassword(options):
    if 'username' in session:
        username = session["username"]
        if options == 0:
            cur.execute(
                "SELECT `password` FROM `user` WHERE `username` = '" + username + "'")
            data = cur.fetchone()
            password = data[0]
            password_bytes = password.encode("ascii")
            sample_string_bytes = base64.b64decode(password_bytes)
            sample_string = sample_string_bytes.decode("ascii")
            # print(sample_string)
            return sample_string
        else:
            return redirect(url_for("login"))


# for calculating total amout
def calcTotalBill():
    sum = 0
    total_amount = 0
    for x in BillProducts:
        cur = x[4]
        sum = sum+cur
        total_amount = sum

    return total_amount

# this formats amounts


def formatNumber(num):
    return ('{:0,d}'.format(num))


# for sending email
def sendEmail(title, recipient, body):
    # check for email in db
    msg = Message(
        title, sender='inventorymanagement777@gmail.com', recipients=[recipient])
    msg.body = body
    mail.send(msg)
    flash("Email sent successfully")

# to update stocks on invoice


def UpdateStockOnInvoice(p_id, p_quantity, opt):
    if 'username' in session:
        username = session["username"]
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
        flash("NEW !! Inventory updated a second ago")
        conn.commit()
    else:
        return redirect(url_for("login"))


# for counting details in inventory

def CountDetailsOfInventory(option):
    if 'username' in session:
        username = session["username"]
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
        if option == 4:
            cur.execute(
                "SELECT SUM(total_amount) FROM `invoice` WHERE `userid` = '" + userid + "'")
        if option == 5:
            cur.execute(
                "SELECT SUM(bill_total) FROM `billing_record` WHERE `userid` = '" + userid + "'")
        if option == 6:
            cur.execute(
                "SELECT Count(productid) FROM `product` WHERE `userid` = '" + userid + "' and `product_instock` <= `product_minlimit`")
        total_product = cur.fetchone()
        return total_product[0]
    else:
        return redirect(url_for("dashboard"))

# function to check stocks


def checkStocks():
    if 'username' in session:
        username = session["username"]
        userid = username
        # this gets all the products from the inventory
        cur.execute(
            "SELECT `product_name`,`productid`,`product_maxlimit`,`product_minlimit`,`product_instock` FROM `product` WHERE `userid` = '" + userid + "'")
        inventory = cur.fetchall()
        # now checking each product for stocks
        for product in inventory:
            # print(product[3])
            if product[4] == 0:
                flash("Product {} with id {} is out of stock".format(
                    product[0], product[1]))
            elif product[4] <= product[3]:
                flash("Product {} with id {} will soon be out of stock".format(
                    product[0], product[1]))
    else:
        return redirect(url_for("dashboard"))

#


def myprofile(option):
    if 'username' in session:
        username = session["username"]
        userid = username
        if option == 1:
            cur.execute(
                "SELECT `name` FROM `user` WHERE `username` = '" + userid + "'")
        if option == 2:
            cur.execute(
                "SELECT `email` FROM `user` WHERE `username` = '" + userid + "'")
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
        cur.execute(
            "SELECT * FROM `user` WHERE `username` = '" + username + "'")
        data = cur.fetchone()
        print(data[0], data[1])
        if data is None:
            flash("Error: User not found or something went wrong!! Try again")
        else:
            if data[0] == username and decrpytpassword(0) == password:
                flash("You logged in successfully ")
                return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pass_word = request.form['pass_word']
        password_bytes = password.encode("ascii")
        base64_bytes = base64.b64encode(password_bytes)
        base64_string = base64_bytes.decode("ascii")
        name = request.form['name']
        email = request.form['email']
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
                                                "%s,%s,%s,%s)", (username, base64_string, name, email, contact_no))
                                    conn.commit()
                                    return render_template("login.html")
                                else:
                                    flash('account created',
                                          category='success')
    return render_template("signup.html")


strUid = ""


@app.route('/forgotPassword', methods=['GET', 'POST'])
def ForgotPassword():
    if request.method == "POST":
        # users email
        email = request.form["email"]
        username = request.form["username"]

        # genrates a unique bill id
        myuuid = uuid.uuid4()
        global strUid
        str1 = str(myuuid)
        strUid = str1[:6]
        print(strUid)
        #
        cur.execute("SELECT `email` FROM `user` WHERE `username` = '" +
                    username + "'")
        User_email = cur.fetchone()
        if User_email[0] != email:
            flash("Give corrrect email id")
            return redirect(url_for("forgotPassword"))
        else:
            sendEmail("Reset Password", email,
                      '\n Your Unique Code for password reset is '+strUid+"\nGo to this link and enter the code to change your password "+'http://127.0.0.1:5000/updatepassword')
            return redirect(url_for("login"))
    return render_template("forgotPassword.html")


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session["username"]
        # calling helper functions
        total_product = CountDetailsOfInventory(1)
        total_suppliers = CountDetailsOfInventory(2)
        total_invoices = CountDetailsOfInventory(3)
        total_Invoicespending = int(CountDetailsOfInventory(4))
        total_earning = int(CountDetailsOfInventory(5))
        total_Lessproduct = int(CountDetailsOfInventory(6))

        # checking if stocks are empty or close to minlimit
        checkStocks()

        return render_template("dashboard.html", username=username, date=displayDate, total_product=total_product, total_suppliers=total_suppliers, total_invoices=formatNumber(total_invoices), total_spending=formatNumber(total_Invoicespending), total_profit=formatNumber(total_earning), product_name=total_Lessproduct)
    else:
        return redirect("login")


@app.route('/dashboard/myprofile')
def profile():
    if 'username' in session:
        username = session["username"]
        Profile_name = myprofile(1)
        Profile_email = myprofile(2)
        Profile_contactno = myprofile(3)
        return render_template("profile.html", username=username, date=displayDate, name=Profile_name, email=Profile_email, contact_no=Profile_contactno)
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
        newInventory = []
        try:
            userid = username
            cur.execute(
                "SELECT * FROM `product` WHERE `userid` = '" + userid + "'")
            inventory = cur.fetchall()
            # now checking for some condition
            for row in inventory:
                newrow = list(row)
                # print(newrow)
                min_limit = newrow[6]
                in_stock = newrow[7]
                if in_stock == 0:
                    newrow.append("Out Of stock")
                    # print("Out")
                elif in_stock <= min_limit:
                    newrow.append("Less stock")
                else:
                    newrow.append("In stock")
                newInventory.append(newrow)
        except:
            flash("Error while getting your inventory")
        return render_template("viewInventory.html", username=username, table=newInventory, date=displayDate)
    else:
        return redirect("login")


@app.route('/dashboard/newInvoice')
def newInvoice():
    if 'username' in session:
        username = session["username"]
        # for view invoice
        list = viewInvoices()
        data = getGetInventoryItem(username)
        return render_template("newInvoice.html", username=username, date=displayDate, supplier_names=data[2], supplier_ids=data[3], product_names=data[0], product_ids=data[1], table=list)
    else:
        return redirect("login")


@app.route('/dashboard/newsuppliers', methods=["GET", "POST"])
def suppliers():
    if 'username' in session:
        username = session["username"]
        list = viewSuppliers()
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
        return render_template("suppliers.html", username=username, date=displayDate, table=list)
    else:
        return redirect("login")


def viewSuppliers():
    if 'username' in session:
        username = session["username"]
        try:
            userid = username
            cur.execute(
                "SELECT * FROM `supplier` WHERE `userid` = '" + userid + "'")
            list = cur.fetchall()
        except:
            flash("Error while getting your suppliers list")
        return list
    else:
        return redirect("login")


@app.route('/deleteSupplier', methods=["GET", "POST"])
def deleteSupplier():
    if 'username' in session:
        username = session["username"]
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


@app.route('/contactUs', methods=["GET", "POST"])
def contactUs():
    if request.method == "POST":
        userid = request.form["username"]
        senderEmail = request.form["email"]
        mailBody = request.form["mail-body"]
        messageDate = displayDate
        # sending email
        msg = Message(
            "From contact form", sender=senderEmail, recipients=['inventorymanagement777@gmail.com'])
        msg.body = mailBody+"\n"+" Received from "+userid+" \n On date "+messageDate
        mail.send(msg)
        flash("Email sent successfully")
    return render_template("contact-page.html")


def convertTuple(tup):
    str = ''.join(tup)
    return str


def getGetInventoryItem(username):
    # for product name
    cur.execute(
        "SELECT `product_name` FROM `product` WHERE `userid` = '" + username + "'")
    ProductsData = cur.fetchall()
    ProductsList = list(ProductsData)

    # for product id
    cur.execute(
        "SELECT `productid` FROM `product` WHERE `userid` = '" + username + "'")
    ProductsIdData = cur.fetchall()
    ProductsIdList = list(ProductsIdData)

    # for supplier id and name
    cur.execute(
        "SELECT `supplier_name` FROM `supplier` WHERE `userid` = '" + username + "'")
    Suppliernames = cur.fetchall()

    cur.execute(
        "SELECT `supplier_id` FROM `supplier` WHERE `userid` = '" + username + "'")
    supplierIds = cur.fetchall()
    return ProductsList, ProductsIdList, Suppliernames, supplierIds


@app.route('/dashboard/billing')
def billing():
    if 'username' in session:
        username = session["username"]
        # getting inventory products
        data = getGetInventoryItem(username)
        return render_template("billing.html", username=username, date=displayDate, products=data[0], productsId=data[1])
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

                # first check if that user is in db or not
                cur.execute("SELECT `supplier_id` FROM `supplier` WHERE `userid` = '" +
                            username + "' AND `supplier_id` = '" + supplier_id + "'")
                supplierId = cur.fetchone()
                supplen = len(supplierId)
                if supplen == None:
                    flash("No supplier found matching with entered supplier ID")
                else:
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


@app.route('/updateStockPrice', methods=["POST"])
def updateStockPrice():
    if 'username' in session:
        username = session["username"]
        if request.method == "POST":
            userid = username
            product_id = request.form['p-id']
            product_price = request.form['p-price']
            cur.execute("UPDATE `product` SET `product_price`= '" + product_price + "' WHERE `userid`= '" +
                        userid + "' and `productid`= '" + product_id + "'")
            conn.commit()
            flash("Price of product ID {} updated successfully".format(product_id))
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
        data = getGetInventoryItem(username)
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
            return render_template("newInvoice.html", username=username, date=displayDate, supplier_names=data[2], supplier_ids=data[3], product_names=data[0], product_ids=data[1])
    else:
        return redirect("login")


@app.route('/dashboard/viewInvoices', methods=["GET"])
def viewInvoices():
    if 'username' in session:
        username = session["username"]
        # all the data from the db will be in tuple in tuple form
        try:
            userid = username
            cur.execute(
                "SELECT * FROM `invoice` WHERE `userid` = '" + userid + "'")
            list = cur.fetchall()
        except:
            flash("Error while getting your suppliers list")
        return list
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
            curProduct = [p_id, p_name, p_quantity,
                          p_price, totalOfProducts, c_name, c_contact]
            global BillProducts
            BillProducts.append(curProduct)
            totalBill = formatNumber(calcTotalBill())
            data = getGetInventoryItem(username)
        except:
            flash("Error while adding to bill ! Try again")
        return render_template("billing.html", username=username, date=displayDate, bill_detail=BillProducts, total_amount=totalBill, bill_items=BillProducts, products=data[0], productsId=data[1])
    else:
        return redirect("login")


totalBill = 0
to_pay = 0


@app.route("/Showbill", methods=["GET"])
def showBill():
    if 'username' in session:
        username = session["username"]
        # this  deletes the products of bill from inventory
        global BillProducts
        for current in BillProducts:
            UpdateStockOnInvoice(current[0], current[2], "sub")

        # this calculates the total bill amount
        global totalBill
        totalBill = calcTotalBill()
        # tax
        global to_pay
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
        print(myuuid)
        strUid = str(myuuid)
        global BillID
        BillID = strUid[0:7]
        # clear the bill product list
        global BillProducts
        BillProducts.clear()
        data = getGetInventoryItem(username)
        return render_template("billing.html", username=username, date=displayDate, bill_detail=BillProducts, billID=BillID, productsId=data[1], products=data[0])
    else:
        return redirect("login")


@app.route('/searchBill', methods=["GET", "POST"])
def searchBill():
    if 'username' in session:
        username = session["username"]
        # get data
        try:
            userid = username
            b_id = request.form['b-id']
            # b_id = '1ba53a7'
            cur.execute("SELECT * FROM `billing_record` WHERE `userid`= '" +
                        userid + "' and `bill_id`='" + b_id+"'")
            billlist = cur.fetchall()
        except:
            flash("Error getting your bill")
        return render_template("billing.html", bills=billlist)
    else:
        return redirect("login")


@app.route('/calcChange', methods=["GET", "POST"])
def calcChange():
    entry = request.form['entry']
    global to_pay
    billAmt = to_pay
    print(billAmt)
    returnMoney = float(entry)-float(billAmt)
    returnTotal = round(returnMoney, 2)
    print(returnTotal)
    return render_template("billing.html", returnMoney=returnTotal)


# calcChange(350, 275.59)


@app.route('/updatepassword', methods=["POST", "GET"])
def Updatepassword():
    if request.method == 'POST':
        try:
            userid = request.form["username"]
            enteredCode = request.form["unique-code"]
            New_password = request.form["password"]
            if enteredCode == strUid:
                New_password_bytes = New_password.encode("ascii")
                base64_bytes = base64.b64encode(New_password_bytes)
                base64_string = base64_bytes.decode("ascii")
                cur.execute("UPDATE `user` SET `password`= '" +
                            base64_string + "' WHERE `username`= '" + userid + "'")
                conn.commit()
                flash("Password of user {} updated successfully".format(userid))
                return redirect(url_for("login"))
            else:
                flash("Entered code doesn't match")
        except:
            flash("Error while getting your password")
    return render_template("resetPassword.html")


@app.route("/deleteuseraccount", methods=["GET", "POST"])
def deleteuser():
    if 'username' in session:
        username = session["username"]
        if request.method == "POST":
            try:
                userid = username
                password = request.form["password"]
                # executing query
                if decrpytpassword(0) != password:
                    flash("Please give correct Password")
                    return redirect(url_for("dashboard"))
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
