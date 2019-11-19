import os
import requests

from flask import Flask, session, render_template, request, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# export FLASk_APP=application.py

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Let user register."""

    # Clear any logged in user
    session.clear()

    if request.method == "POST":

        # Ensure username and passwords were submitted
        if not request.form.get("password") or not request.form.get("password2") or not request.form.get("name"):
            return render_template("error.html", message="Vul alle velden in.")

        # Ensure passwords are the same
        if request.form.get("password") != request.form.get("password2"):
            return render_template("error.html", message="Wachtwoorden komen niet overeen.")

        # Get form information.
        try:
            db.execute("INSERT INTO names (name, hash) VALUES (:name, :hash)",
                        {"name": request.form.get("name"),
                        "hash": generate_password_hash(request.form.get("password"))})
            db.commit()
        except:
            return render_template("error.html", message="TODO: super leuke error.")

        # Query database for username
        rows = db.execute("SELECT * FROM names WHERE name = :name",
                          {"name": request.form.get("name")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", message="Deze inlognaam is al in gebruik")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["name"] = rows[0]["name"]

        return render_template("home.html")

    else:
        return render_template("register.html")


@app.route("/home", methods=["GET", "POST"])
def login():
    """Let user login."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("name"):
            return render_template("error.html", message="Vul je naam in.")

        if not request.form.get("password"):
            return render_template("error.html", message="Vul je wachtwoord in.")

        # Query database for username
        rows = db.execute("SELECT * FROM names WHERE name = :name",
                          {"name": request.form.get("name")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", message="Inloggegevens zijn incorrect.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["name"] = rows[0]["name"]

        # return render_template("welcome.html")
        return render_template("welcome.html", name=rows[0]["name"])

    return render_template("home.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id (LOGOUT)
    session.clear()

    # Redirect user to login form
    return render_template("home.html")


@app.route("/books", methods=["GET", "POST"])
@login_required
def books():
    """Look up books"""

    if request.method == "POST":

        # Create dictionary for books' characteristics
        books = {}

        try:
            book = db.execute("SELECT * FROM books WHERE isbn LIKE :book OR \
                                title LIKE :book OR \
                                author LIKE :book OR \
                                year LIKE :book ORDER BY title",
                             {"book": "%" + request.form.get("book") + "%"} ).fetchall()
        except:
            return render_template("error.html")

        if not book:
            flash("Nothing found, SORRY!!!!!!! :( ")

        # Dictionary for isbn, title, author and year.
        for i in range(0, len(book)):
            d = {"isbn": book[i][0], "titel": book[i][1], "auteur": book[i][2], "jaar": book[i][3]}
            books.update({i: d})

        return render_template("books.html", book=books)

    else:

        return render_template("books.html", book="")


@app.route("/history/<book_id>", methods=["GET", "POST"])
@login_required
def history(book_id):
    """Detailed information about a book."""

    if request.method == "GET":

        # Get book information.
        book = db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn": book_id}).fetchone()
        books = {"isbn": book[0], "titel": book[1], "auteur": book[2], "jaar": book[3]}

        # Check if this user has a review for this book
        review = db.execute("SELECT * FROM review WHERE id=:id and isbn=:isbn",
                            {"id": session["user_id"],
                            "isbn": book_id}).fetchone()

        if not review:
            review = ""

        # Get API data
        average_rating, ratings_count = getAPIdata(book_id)

        return render_template("history.html", book=books, review=review,
                                average_rating=average_rating, ratings_count=ratings_count)

    else:

        # Get book information.
        book = db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn": book_id}).fetchone()
        books = {"isbn": book[0], "titel": book[1], "auteur": book[2], "jaar": book[3]}

        # Check if this user has a review for this book
        review = db.execute("SELECT * FROM review WHERE isbn=:isbn",
                            {"id": session["user_id"],
                            "isbn": book_id}).fetchone()

        if not review:

            # Check length of review
            if len(request.form.get('review')) < 250:

                # Insert new review
                db.execute("INSERT INTO review (booktitle, id, reviewtitle, rating, review, isbn) \
                            VALUES (:booktitle, :id, :reviewtitle, :rating, :review, :isbn); ",
                            {"booktitle": books["titel"],
                            "id": session["user_id"],
                            "reviewtitle": request.form.get('reviewtitle'),
                            "rating": request.form.get('rating'),
                            "review": request.form.get('review'),
                            "isbn": book_id })
                db.commit()

                reviews = db.execute("SELECT * FROM review WHERE isbn=:isbn",
                                    {"isbn": book_id}).fetchall()

                flash("Review saved!", "info")
                return render_template("reviews.html", reviews=reviews)

            else:
                flash("Your review is too long! :(")
                return redirect("/history/" + book_id)


@app.route("/reviews", methods=["GET", "POST"])
@login_required
def reviews():
    """History of reviews."""

    if request.method == "GET":

        # Select all reviews for this person
        reviews = db.execute("SELECT * FROM review WHERE id=:id",
                            {"id": session["user_id"]}).fetchall()

        if not reviews:
            reviews = None

        return render_template("reviews.html", reviews=reviews)


@app.route("/api/<isbn>", methods=["GET"])
@login_required
def api(isbn):

    # Get book information
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    if not book:
        return jsonify({"Error": "Invalid book ISBN"}), 422

    average_rating, ratings_count = getAPIdata(isbn)

    return jsonify(
        title=book[1],
        author=book[2],
        year=book[3],
        isbn=book[0],
        ratings_count=ratings_count,
        average_rating=average_rating
    )


def getAPIdata(isbn):
    """ Get average rating and ratings count from API. """

    # Get json data
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
          params={"key": "rWteR2GkTAr1DwQDIqdzw", "isbns": isbn})

    # Check for succesful load of API request
    if res.status_code == 200:
        res = res.json()["books"][0]
        average_rating, ratings_count = res["average_rating"], res["ratings_count"]
    else:
        flash("Goodreads details could not be loaded.", "warning")
        average_rating, ratings_count = "", ""

    return average_rating, ratings_count
