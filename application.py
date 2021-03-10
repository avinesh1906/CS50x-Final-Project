import os
import datetime
import calendar

from cs50 import SQL
from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helper import apology, cardvalidation, login_required, password_validation, findDay

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///expenses.db")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Missing password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        flash("Welcome")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")

        # ensure username is submitted
        if not username:
            return apology("Missing username")

        # ensure password is submiited
        elif not request.form.get("password"):
            return apology("Missing password")

        # ensure confirmed password is submitted
        elif not request.form.get("confirmation"):
            return apology("Insert password again")

        # validate password
        elif password_validation(request.form.get("password")) == -1:
            return apology("Password should be at least 8 characters long including letters and numbers")

        # check for matching password
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password does not match")

        # validate paybal number
        elif not request.form.get("paybalnum"):
            if cardvalidation(int(request.form.get("cardnum"))) == -1:
                return apology("Enter a valid card number")

        # ensure checkbox is ticked
        elif not request.form.get("check"):
            return apology("Cannot register if does not accept Terms and Condtions")

        # hash password
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        data = db.execute("SELECT * FROM users")

        for row in data:
            # check if username already taken
            if row["username"] == username:
                return apology("Username already taken")

        # register user
        db.execute("INSERT INTO users (username, hash, cardnum, paybalnum) VALUES (:username, :password, :cardnum, :paybalnum)",
                   username=username, password=password, cardnum=request.form.get("cardnum"), paybalnum=request.form.get("paybalnum"))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/")
@login_required
def index():
    """  Display home page """
    purchase = db.execute("SELECT * FROM purchase WHERE id= :id", id=session["user_id"])

    # for purchase type
    if len(purchase) == 0:
        datadict = {
            "Type": "Number of type",
            "Groceries": 1,
            "Leisure and Entertainment": 1,
            "Others": 1
        }
    else:
        datadict = {
            "Type": "Number of type",
            "Groceries": 0,
            "Leisure and Entertainment": 0,
            "Others": 0
        }
    for row in purchase:
        if row["type"] == "Groceries":
            datadict["Groceries"] += row["numberoftype"]
        elif row["type"] == "Leisure and Entertainment":
            datadict["Leisure and Entertainment"] += row["numberoftype"]
        elif row["type"] == "Others":
            datadict["Others"] += row["numberoftype"]

    # for weekkly total purchase
    dataweekdict = {
        "Days": "Total money spent $",
        "Mon": 0,
        "Tue": 0,
        "Wed": 0,
        "Thur": 0,
        "Fri": 0,
        "Sat": 0,
        "Sun": 0
    }
    history = db.execute("SELECT * FROM history WHERE id= :id AND category = :category", id=session["user_id"], category="purchase")

    week_num = datetime.date.today().isocalendar()[1]

    for rows in history:
        string = rows["date"]
        date = string.split("-")
        week_number = int(datetime.date(int(date[0]), int(date[1]), int(date[2])).strftime("%V"))
        day = findDay(string)
        if week_number == week_num:
            if day == "Monday":
                dataweekdict["Mon"] += int(rows["price"])

            elif day == "Tuesday":
                dataweekdict["Tue"] += int(rows["price"])

            elif day == "Wednesday":
                dataweekdict["Wed"] += int(rows["price"])

            elif day == "Thursday":
                dataweekdict["Thur"] += int(rows["price"])

            elif day == "Friday":
                dataweekdict["Fri"] += int(rows["price"])

            elif day == "Saturday":
                dataweekdict["Sat"] += int(rows["price"])

            elif day == "Sunday":
                dataweekdict["Sun"] += int(rows["price"])
        else:
            dataweekdict = {
                "Days": "Total money spent $",
                "Mon": 0,
                "Tue": 0,
                "Wed": 0,
                "Thur": 0,
                "Fri": 0,
                "Sat": 0,
                "Sun": 0
            }

    # for payment type
    if len(purchase) == 0:
        adataweekdict = {
            "Payment Type": "Number of time used",
            "Card": 1,
            "Cash": 1,
            "Paypal": 1
        }
    else:
        adataweekdict = {
            "Payment Type": "Number of time used",
            "Card": 0,
            "Cash": 0,
            "Paypal": 0
        }
    paymenttype1 =db.execute("SELECT * FROM paymenttype WHERE id = :id", id=session["user_id"])
    for rowk in paymenttype1:
        stringk = rowk["date"]
        datek = stringk.split("-")
        week_numberk = int(datetime.date(int(datek[0]), int(datek[1]), int(datek[2])).strftime("%V"))
        if week_numberk == week_num:
            if rowk["paymenttype"] == "Card":
                adataweekdict["Card"] += 1
            elif rowk["paymenttype"] == "Cash":
                adataweekdict["Cash"] += 1
            elif rowk["paymenttype"] == "Paypal":
                adataweekdict["Paypal"] += 1

    # for monthly total purchase
    janlst = [0, 0, 0, 0]
    feblst = [0, 0, 0, 1]
    marlst = [0, 0, 0, 2]
    aprlst = [0, 0, 0, 3]
    maylst = [0, 0, 0, 4]
    junlst = [0, 0, 0, 5]
    jullst = [0, 0, 0, 6]
    auglst = [0, 0, 0, 7]
    seplst = [0, 0, 0, 8]
    octlst = [0, 0, 0, 9]
    novlst = [0, 0, 0, 10]
    declst = [0, 0, 0, 11]

    datamonthdict = {
        "Month": "Total money spent per month",
        "JAN": janlst,
        "FEB": feblst,
        "MARCH": marlst,
        "APR": aprlst,
        "MAY": maylst,
        "JUNE": junlst,
        "JULY": jullst,
        "AUG": auglst,
        "SEPT": seplst,
        "OCT": octlst,
        "NOV": novlst,
        "DEC": declst,
    }

    history = db.execute("SELECT * FROM history WHERE id= :id AND category = :category", id=session["user_id"], category="purchase")

    for rowb in history:
        stringb = rowb["date"]
        dateb = stringb.split("-")
        print(dateb)
        if dateb[1] == "01":

            if rowb["type"] == "Groceries":
                janlst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                janlst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                janlst[2] += int(rowb["price"])

        elif dateb[1] == "02":

            if rowb["type"] == "Groceries":
                feblst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                feblst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                feblst[2] += int(rowb["price"])

        elif dateb[1] == "03":

            if rowb["type"] == "Groceries":
                marlst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                marlst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                marlst[2] += int(rowb["price"])

        elif dateb[1] == "04":

            if rowb["type"] == "Groceries":
                aprlst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                aprlst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                aprlst[2] += int(rowb["price"])

        elif dateb[1] == "05":

            if rowb["type"] == "Groceries":
                maylst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                maylst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                maylst[2] += int(rowb["price"])

        elif dateb[1] == "06":

            if rowb["type"] == "Groceries":
                junlst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                junlst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                junlst[2] += int(rowb["price"])

        elif dateb[1] == "07":

            if rowb["type"] == "Groceries":
                jullst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                jullst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                jullst[2] += int(rowb["price"])

        elif dateb[1] == "08":
            if rowb["type"] == "Groceries":
                auglst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                auglst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                auglst[2] += int(rowb["price"])

        elif dateb[1] == "09":

            if rowb["type"] == "Groceries":
                seplst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                seplst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                seplst[2] += int(rowb["price"])

        elif dateb[1] == "10":

            if rowb["type"] == "Groceries":
                octlst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                octlst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                octlst[2] += int(rowb["price"])

        elif dateb[1] == "11":

            if rowb["type"] == "Groceries":
                novlst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                novlst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                novlst[2] += int(rowb["price"])

        elif dateb[1] == "12":

            if rowb["type"] == "Groceries":
                declst[0] += int(rowb["price"])
            elif rowb["type"] == "Leisure and Entertainment":
                declst[1] += int(rowb["price"])
            elif rowb["type"] == "Others":
                declst[2] += int(rowb["price"])

    return render_template("index.html", data=datadict, dataweek=dataweekdict, datapayment=adataweekdict, datatotal=datamonthdict)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    row = db.execute("SELECT * FROM history WHERE id = :id ORDER BY date DESC", id=session["user_id"])
    return render_template("history.html", rows=row)


@app.route("/insert", methods=["GET", "POST"])
@login_required
def insert():
    if request.method == "POST":

        if not request.form.get("price"):
            return apology("Missing price")
        elif not request.form.get("date"):
            return apology("Missing date")
        elif not request.form.get("type"):
            return apology("Missing type")
        elif not request.form.get("paymenttype"):
            return apology("Missing payment type")
        elif not request.form.get("numberoftype"):
            return apology("Missing number of refund item")

        stock = db.execute("SELECT * FROM purchase WHERE id = :id AND type = :type AND paymenttype = :paymenttype",
                           id=session["user_id"], type=request.form.get("type"), paymenttype=request.form.get("paymenttype"))

        if len(stock) == 0:
            db.execute("INSERT INTO purchase (id, price, type, numberoftype, paymenttype) VALUES (:id, :price, :type, :count, :paymenttype)",
                       id=session["user_id"], price=int(request.form.get("price")), type=request.form.get("type"), count=request.form.get("numberoftype"), paymenttype=request.form.get("paymenttype"))

        else:
            db.execute("UPDATE purchase SET numberoftype = numberoftype + :count, paymenttype = paymenttype + :pay, price = price + :price WHERE id = :id AND type = :type",
                       type=request.form.get("type"), id=session["user_id"], pay=request.form.get("paymenttype"), count=request.form.get("numberoftype"), price=int(request.form.get("price")))

        db.execute("INSERT INTO history (id,date,price,type, category) VALUES (:id, :date, :price, :type, :category) ",
                   id=session["user_id"], date=request.form.get("date"), price=str(request.form.get("price")), type=request.form.get("type"), category="purchase")
        db.execute("INSERT INTO paymenttype (id,paymenttype,date) VALUES (:id, :pay, :date)", id=session["user_id"], pay=request.form.get("paymenttype") , date=request.form.get("date"))

        return redirect("/")
    else:
        return render_template("insert.html")


@app.route("/refund", methods=["GET", "POST"])
@login_required
def refund():

    if request.method == "POST":
        if not request.form.get("type"):
            return apology("Missing type")

        elif not request.form.get("date"):
            return apology("Missing date")

        elif not request.form.get("price"):
            return apology("Missing price")

        elif not request.form.get("refundtype"):
            return apology("Missing refund type")

        elif not request.form.get("numberoftype"):
            return apology("Missing number of refund item")

        stock = db.execute("SELECT * FROM purchase WHERE id= :id AND type = :type",
                           id=session["user_id"], type=request.form.get("type"))

        if len(stock) == 0:
            return apology("Had not done any purchase of this type before, REFUND is not possible")
        elif int(request.form.get("numberoftype")) > stock[0]["numberoftype"]:
            return apology("Cannot refund more than purchased")

        stock = db.execute("SELECT * FROM refund WHERE id = :id AND type = :type",
                           id=session["user_id"], type=request.form.get("type"))

        if len(stock) == 0:
            db.execute("INSERT INTO refund (id, price, type, numberoftype,refundtype) VALUES (:id, :price, :type, :count, :refundtype)",
                       id=session["user_id"], price=int(request.form.get("price")), type=request.form.get("type"), count=request.form.get("numberoftype"), refundtype=request.form.get("refundtype"),)
        else:
            db.execute("UPDATE refund SET numberoftype = numberoftype + :count, price = price + :price WHERE id = :id AND type = :type",
                       type=request.form.get("type"), id=session["user_id"], count=request.form.get("numberoftype"), price=int(request.form.get("price")))

        db.execute("INSERT INTO history (id,date,price,type, category) VALUES (:id, :date, :price, :type, :category) ",
                   id=session["user_id"], date=request.form.get("date"), price=str(request.form.get("price")), type=request.form.get("type"), category="refund")

        return redirect("/")
    else:
        return render_template("refund.html")


@app.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    if request.method == "GET":
        return render_template("setting.html")


@app.route("/changeusername", methods=["GET", "POST"])
@login_required
def changeusername():
    if request.method == "POST":

        username = request.form.get("username")
        if not username:
            return apology("Missing username")

        data = db.execute("SELECT * FROM users")

        for row in data:
            if row["username"] == username:
                return apology("Username already taken")

        db.execute("UPDATE users SET username = :username WHERE  id = :id", username=username, id=session["user_id"])

        return redirect("/")
    else:
        username = db.execute("SELECT username FROM users WHERE id = :id", id=session["user_id"])
        for row in username:
            user = row["username"]
        return render_template("changeusername.html", username = user)


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    if request.method == "POST":

        if not request.form.get("oldpassword"):
            return apology("Missing password")

        elif not request.form.get("newpassword"):
            return apology("Missing password")

        elif not request.form.get("confirmation"):
            return apology("Insert password again")

        elif password_validation(request.form.get("newpassword")) == -1:
            return apology("Password should be at least 8 characters long including letters and numbers")

        elif request.form.get("newpassword") == request.form.get("oldpassword"):
            return apology("New password should be different from old")

        elif request.form.get("newpassword") != request.form.get("confirmation"):
            return apology("Password does not match")

        data = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])

        if not check_password_hash(data[0]["hash"], request.form.get("oldpassword")):
            return apology("Enter the correct old password")

        password = generate_password_hash(request.form.get("newpassword"), method='pbkdf2:sha256', salt_length=8)

        db.execute("UPDATE users SET hash = :password WHERE  id = :id", password=password, id=session["user_id"])

        return redirect("/")

    else:
        return render_template("changepassword.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

