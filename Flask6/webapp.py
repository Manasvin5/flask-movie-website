from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from mysql.connector import connect
import requests

webapp = Flask(__name__)


webapp.config['MYSQL_HOST'] = 'localhost'
webapp.config['MYSQL_USER'] = 'root'
webapp.config['MYSQL_PASSWORD'] = ''
webapp.config['MYSQL_DB'] = 'flask_app'


mysql = MySQL(webapp)


webapp.secret_key = 'your_secret_key'

"""
    A route handler for the index page, handling both GET and POST requests. 
    It takes no parameters and returns rendered HTML using the index.html template.
"""
@webapp.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            movies = search_movie(query)
            return render_template("index.html", movies=movies)

    return render_template("index.html", movies=[])

@webapp.route("/movie/<movie_id>")
def movie_details(movie_id):
    movie = get_movie_details(movie_id)
    return render_template("movie_details.html", movie=movie)

@webapp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_id = request.form['user_id']

        conn = connect(
            host='localhost',
            user='root',
            password='',
            database='flask_app'
        )
        cur = conn.cursor(dictionary=True)

        cur.execute("INSERT INTO user_info (username, password, email, user_id) VALUES (%s, %s, %s, %s)",
                    (username, password, email, user_id))
        cur.execute(f"CREATE TABLE IF NOT EXISTS {username}_watched_movies "
            "(id INT AUTO_INCREMENT PRIMARY KEY, movie_name VARCHAR(255), imdbID VARCHAR(20) UNIQUE, year INT, runtime BIGINT)")
        conn.commit()
        cur.close()
        conn.close()

        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))

    return render_template("register.html")

@webapp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = connect(
            host='localhost',
            user='root',
            password='',
            database='flask_app'
        )
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM user_info WHERE username = %s AND password = %s", (username, password))
        

        
        result = cur.fetchone()

        if result:
            session['logged_in'] = True
            session['username'] = result['username']
            flash('You are now logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

        cur.close()
        conn.close()

    return render_template("login.html")

@webapp.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

def search_movie(query):
    base_url = "http://www.omdbapi.com/"
    params = {
        "apikey": "e8c9b6ee", 
        "s": query,
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    return data.get("Search", [])

def get_movie_details(movie_id):
    base_url = "http://www.omdbapi.com/"
    params = {
        "apikey": "e8c9b6ee", 
        "i": movie_id,
    }

    response = requests.get(base_url, params=params)
    return response.json()


def create_watched_movies_table(username):
    conn = connect(
        host='localhost',
        user='root',
        password='',
        database='flask_app'
    )
    cur = conn.cursor()
    
    try:
        cur.execute(f"CREATE TABLE IF NOT EXISTS {username}_watched_movies "
                    "(id INT AUTO_INCREMENT PRIMARY KEY, movie_name VARCHAR(255), imdbID VARCHAR(20) UNIQUE, year INT, runtime BIGINT)")
        conn.commit()
    except Exception as e:
        # Handle the exception (e.g., log it, flash a message, etc.)
        print(f"Error creating table for {username}: {e}")
    finally:
        cur.close()
        conn.close()

@webapp.route("/watched_movies", methods=["GET"])
@webapp.route("/watched_movies")
def watched_movies():
    if 'username' in session:
        username = session['username']

        conn = connect(
            host='localhost',
            user='root',
            password='',
            database='flask_app'
        )
        cur = conn.cursor(dictionary=True)

        try:
            # Fetch watched movies from the user's table
            cur.execute(f"SELECT * FROM {username}_watched_movies")
            watched_movies = cur.fetchall()

            # Fetch additional details (including posters) from OMDB API
            total_runtime = sum(movie['runtime'] for movie in watched_movies)

            for movie in watched_movies:
                movie_details = get_movie_details(movie['imdbID'])
                movie['Poster'] = movie_details.get('Poster', '')  

            return render_template("watched_movies.html", watched_movies=watched_movies, total_runtime=total_runtime)
        except Exception as e:
            # Handle the exception (e.g., log it, flash a message, etc.)
            print(f"Error fetching watched movies for {username}: {e}")
        finally:
            cur.close()
            conn.close()

    flash('You need to be logged in to view watched movies.', 'danger')
    return redirect(url_for('login'))



@webapp.route("/mark_as_watched/<movie_id>", methods=["POST"])
def mark_as_watched(movie_id):
    if 'username' in session:
        username = session['username']

        
        movie_details = get_movie_details(movie_id)
        #numeric runtime value
        runtime_str = movie_details['Runtime']
        runtime = int(''.join(filter(str.isdigit, runtime_str)))

        
        conn = connect(
            host='localhost',
            user='root',
            password='',
            database='flask_app'
        )
        cur = conn.cursor()

        cur.execute(f"INSERT INTO {username}_watched_movies (movie_name, imdbID, year, runtime) "
                    "VALUES (%s, %s, %s, %s)",
                    (movie_details['Title'], movie_details['imdbID'], movie_details['Year'], runtime))
        conn.commit()
        cur.close()
        conn.close()

        flash(f"{movie_details['Title']} marked as watched!", 'success')
    else:
        flash('You need to be logged in to mark movies as watched.', 'danger')

    return redirect(url_for('movie_details', movie_id=movie_id))

if __name__ == "__main__":
    webapp.run(debug=True,host='0.0.0.0', port=8001)
