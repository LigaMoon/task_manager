import os
from flask import (Flask, flash, render_template, redirect, request, url_for, session)
from flask_pymongo import PyMongo
# MongoDB stores data in json like format - bson so we need to import the below
from bson.objectid import ObjectId
# Security features used in login page
from werkzeug.security import generate_password_hash, check_password_hash
# only import env if env.py file path can be found 
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

# adding database name, database link and secret key environment variables, these need to be set in env.py file and in heroku
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# Creating an instance of pymongo with a constructor method
mongo = PyMongo(app)


@app.route('/')
# Make a connection to the database whenever .../get_tasks is accessed
# Because get_tasks is directly under '/', it will be called as default
@app.route('/get_tasks')
def get_tasks():
    # will render tasks.html file that has to be placed in the templates folder!!
    # Then assign tasks to 'tasks' collection under task_manager database and find() will return everything that's in it (mongo=PyMongo(app))
    # convert to list so that it can be used more than once on an html file and commented out
    tasks  = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks = tasks)


# Bring the user to register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Succesful")
        return redirect(url_for('profile', username = session["user"]))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # check if username exists in db and return that record as a dictionary or user and password
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # If there is a user that match entered username
        if existing_user:
            # ensure hashed password matches user input, it takes 2 variables, first is password from the returned dictionary above, the second is entered password, both are compared
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for('profile', username = session["user"]))
            else:
                # Invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))
            
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Grab the sessions user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    # only show profile if a session cookie exists and user has been logged it, this will avoid others using  usernames to access profiles
    if session["user"]:
        return render_template("profile.html", username = username)
        
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # Remove user from session cookies by logging out
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for('login'))


# Add task on this route and use categories catallog to display categories 
@app.route('/add_task', methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        task={
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(task)
        flash("Task succesfully Added")
        return redirect(url_for("get_tasks"))

    categories = mongo.db.categories.find().sort("category_name",1)
    return render_template('addtasks.html', categories = categories )


# When a task is submitted on the add_task page, it is posted to insert_task which inserts data in the tasks collection and converts data to a dictionary. Once done it redirects the user to the get_task page and newly added task is dipslayed
# @app.route('/insert_task', methods=['POST'])
# def insert_task():
#     # new variable that equates the tasks collection
#     tasks = mongo.db.tasks
#     tasks.insert_one(request.form.to_dict())
#     return redirect(url_for('get_tasks'))

# Once a specific task with task_id = _id is accessed, task equals to that specific task (only one).
@app.route('/edit_task/<task_id>', methods=["GET", "POST"])
def edit_task(task_id):
    # Returns task id
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("catedgory_name",1)
    return render_template('edittasks.html', task = task, categories = categories)

@app.route('/update_task/<task_id>', methods=["POST"])
def update_task(task_id):
    tasks = mongo.db.tasks
    tasks.update( {'_id': ObjectId(task_id)},
    { 
        'task_name': request.form.get('task_name'),
        'category_name': request.form.get('category_name'),
        'task_description': request.form.get('task_description'),
        'due_date': request.form.get('due_date'),
        'is_urgent': request.form.get('is_urgent')
    })
    return redirect(url_for('get_tasks'))

@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    mongo.db.tasks.remove({'_id': ObjectId(task_id)})
    return redirect(url_for('get_tasks'))

if __name__ == '__main__':
    app.run(host = os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)