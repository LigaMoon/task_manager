import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
# MongoDB stores data in json like format - bson so we need to import the below
from bson.objectid import ObjectId

app = Flask(__name__)

# adding database name and a link to the database (this is optional but is a good idea to iknclude)
app.config["MONGO_DBNAME"] = 'task_manager'
#set it as an environ var in heroku as well as lolcal machine
app.config["MONGO_URI"] = os.getenv('MONGO_URI_TASK')

# Creating an instance of pymongo with a constructor method
mongo = PyMongo(app)

@app.route('/')
# Make a connection to the database whenever .../get_tasks is accessed
# Because get_tasks is directly under '/', it will be called as default
@app.route('/get_tasks')
def get_tasks():
    # will render tasks.html file that has to be placed in the templates folder!!
    # Then assign tasks to 'tasks' collection under task_manager database and find() will return everything that's in it (mongo=PyMongo(app))
    return render_template("tasks.html", tasks = mongo.db.tasks.find())

if __name__ == '__main__':
    app.run(host = os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)