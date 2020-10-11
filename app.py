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

# Add task on this route and use categories catallog to display categories 
@app.route('/add_task')
def add_task():
    return render_template('addtasks.html', categories=mongo.db.categories.find())

# When a task is submitted on the add_task page, it is posted to insert_task which inserts data in the tasks collection and converts data to a dictionary. Once done it redirects the user to the get_task page and newly added task is dipslayed
@app.route('/insert_task', methods=['POST'])
def insert_task():
    # new variable that equates the tasks collection
    tasks = mongo.db.tasks
    tasks.insert_one(request.form.to_dict())
    return redirect(url_for('get_tasks'))

# Once a specific task with task_id = _id is accessed, task equals to that specific task (only one).
@app.route('/edit_task/<task_id>')
def edit_task(task_id):
    # Returns task id
    the_task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    all_categories = mongo.db.categories.find()
    return render_template('edittasks.html', task = the_task, categories = all_categories)

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