import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import apology, login_required, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kingsexp.db")




@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("SELECT game_date, event, a.name, b.description, sum(quantity) as quantity FROM transactions a INNER JOIN experiences b on a.name = b.name where id = :id GROUP BY game_date, event, a.name, b.description HAVING sum(quantity) > 0", id = session["user_id"])
    users = db.execute("SELECT cash, first_name FROM users WHERE id = :id", id = session["user_id"])
    cash = round(users[0]["cash"], 2)
    first_name = users[0]["first_name"]
    if not rows:
        return redirect("/buy")
    else:
        for row in rows:
            name = row["name"]
            event = row["event"]
            quantity = row["quantity"]
            game_date = row["game_date"]
            description = row['description']

        return render_template("index.html", users=users, rows=rows, name=name, event=event, quantity=quantity, game_date=game_date, first_name = first_name, cash=cash, description = description)




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # ensure that a symbol was typed in.
        if not request.form.get("name"):
            return apology("symbol required")


        # ensure that a quantity of shares was typed in.
        if not request.form.get("quantity"):
            return apology("quantity required")


        # try to cast shares as integer
        try:
            quantity = int(request.form.get("quantity"))
        except:
            return apology("Quantity must be an integer")

        if request.form.get("quantity").isdigit() == False:
            return apology("quantity must be a positive value")

        # write query via db.execute to find currect cash held by user

        users = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        rows = db.execute("Select name, description, price FROM experiences WHERE name = :name", name = request.form.get("name"))
        games = db.execute("Select event, game_date FROM games where game_date > date('now')")

        cash = users[0]["cash"]
        quantity = request.form.get("quantity")
        name = request.form.get("name")
        game_long = request.form.get("game_long")
        game_date = game_long.split(" | ")[1]
        event = game_long.split(" | ")[0]

        for row in rows:
            description = row["description"]
            price = row["price"]

        # calculate total price
        total_price = float(quantity) * price

        # check that user has enough money.
        if total_price > users[0]["cash"]:
            return apology("you do not have enough cash for purchase")

        else:
            # Insert transaction into transactions table
            db.execute("INSERT INTO transactions (name, quantity, price, id, game_date, event, add_date) VALUES(:name, :quantity, :price, :user_id, :game_date, :event, datetime('now'));",
            name = name, quantity = quantity, price = price, user_id = session["user_id"], game_date = game_date, event = event)
        # deduct the price from total cash, and update the current user's cash value in user table.
        db.execute("UPDATE users SET cash = cash - :total_price WHERE id = :user_id",
        total_price = total_price, user_id = session["user_id"])

        return redirect("/")

    # if get instead of post, send to buy.html
    else:
        rows = db.execute("Select name, description, price FROM experiences ORDER BY price desc")
        games = db.execute("Select event, game_date FROM games where game_date > date('now')")
        for row in rows:
            name = row["name"]
        for game in games:
            event = game["event"] + '' + game['game_date']

        users = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        cash = users[0]["cash"]

        return render_template("buy.html", rows=rows, name=name, event=event, games = games, users = users, cash = cash)



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", "Oops")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure password confirmation was submitted
        elif not request.form.get("password2"):
            return apology("must provide password confirmation")

        # Ensure password matches password confirmation
        elif request.form.get("password") != request.form.get("password2"):
            return apology("password confirmation must match password")

        # Ensure password has at least eight characters
        elif len(request.form.get("password")) < 8:
            return apology("password must be at least 8 characters")

        # Insert Row Into Database
        hash = generate_password_hash(request.form.get("password"))
        result = db.execute("INSERT INTO users (username, hash, first_name, last_name) VALUES(:username, :hash, :first_name, :last_name)",
            username=request.form.get("username"), hash=hash, first_name=request.form.get("first_name"),last_name=request.form.get("last_name"))

        if not result:
            return apology("The username is already taken")

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect('/')

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
    # ensure that a symbol was typed in.
        if not request.form.get("name_long"):
            return apology("must select an experience to return")


        # ensure that a quantity of shares was typed in.
        if not request.form.get("quantity"):
            return apology("quantity required")


        # try to cast shares as integer
        try:
            quantity = int(request.form.get("quantity"))
        except:
            return apology("Quantity must be an integer")

        if request.form.get("quantity").isdigit() == False:
            return apology("quantity must be a positive value")

        # write query via db.execute to find currect cash held by user
        name_long = request.form.get("name_long")
        event = name_long.split('_')[0]
        name = name_long.split('_')[2]
        game_date = name_long.split('_')[1]

        users = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        rows = db.execute("Select name, description, price FROM experiences WHERE name = :name", name = request.form.get("name"))
        games = db.execute("Select event, game_date FROM games where game_date > date('now')")
        inventory = db.execute("Select event, game_date, name, price, sum(quantity) as quantity FROM transactions where id = :id and event = :event and name = :name and game_date = :game_date GROUP BY event, game_date, name, price HAVING sum(quantity) > 0", id = session["user_id"], name = name, event = event, game_date = game_date)

        cash = users[0]["cash"]
        quantity = 0 - int(request.form.get("quantity"))
        for item in inventory:
            if item["quantity"] < int(request.form.get("quantity")):
                    return apology("You do not have enough of this item to sell")
            else:
                price = 0 - item["price"]
                total_price = int(request.form.get("quantity")) * item["price"]
                # Insert transaction into transactions table
                db.execute("INSERT INTO transactions (name, quantity, price, id, game_date, event, add_date) VALUES(:name, :quantity, :price, :user_id, :game_date, :event, datetime('now'));",
                name = name, quantity = quantity, price = price, user_id = session["user_id"], game_date = game_date, event = event)
                # deduct the price from total cash, and update the current user's cash value in user table.
                db.execute("UPDATE users SET cash = cash + :total_price WHERE id = :user_id",
                total_price = total_price, user_id = session["user_id"])

            return redirect("/")
    else:
        inventory = db.execute("Select name, event, game_date,sum(quantity) as quantity FROM transactions where id = :id GROUP BY name, event, game_date HAVING sum(quantity) > 0 ORDER BY game_date", id = session["user_id"])
        users = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        for item in inventory:
            name = item["name"]
            event = item["event"]
            game_date = item["game_date"]
        return render_template("sell.html", inventory=inventory, name=name, event=event, game_date = game_date)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
