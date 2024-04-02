from flask import request
from . import app, db
from .models import User, Task
from .auth import basic_auth, token_auth

#Define route
@app.route('/')
def index():
    return 'Task API'

#Create user
@app.route('/users', methods=['POST'])
def  create_user():
    if not request.is_json:
        return {'error': f"Content-type must be application/json"},400
    data = request.json
    required_fields = ['username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
            return {'error': "A user with that username and/or email already exists"}, 400
        
    new_user = User(username=username, email=email, password=password)
    
    return new_user.to_dict(), 201

#Token auth
@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()

#Return all tasks as JSON object
@app.route('/tasks')
def get_tasks():
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where((Task.title.ilike(f"%{search}%")) | (Task.description.ilike(f"%{search}%"))) #searches in title or body
    # Get the tasks from the database
    tasks = db.session.execute(select_stmt).scalars().all()
    return [p.to_dict() for p in tasks]

#Return all users as JSON object
@app.route('/users')
def get_users():
    select_stmt = db.select(User)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where((User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))) #searches in username or email
    # Get the tasks from the database
    users = db.session.execute(select_stmt).scalars().all()
    return [p.to_dict() for p in users]

#Get a single task by ID
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    # Get the task from the database by ID
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"Task with an ID of {task_id} does not exist"}, 404
    
#Get a single user by ID
@app.route('/users/<int:user_id>')
def get_user(user_id):
    # Get the task from the database by ID
    user = db.session.get(User, user_id)
    if user:
        return user.to_dict()
    else:
        return {'error': f"User with an ID of {user_id} does not exist"}, 404

#Create a task
@app.route('/tasks', methods=['POST'])
@token_auth.login_required
def create_task():
    
    #check if json
    if not request.is_json:
        return {'error': f"Content-type must be application/json"},400
    data = request.json
    
    #check for required fields
    required_fields = ['title', 'description', 'dueDate']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"},400
    
    title = data.get('title')
    description = data.get('description')
    completed = False
    dueDate = data.get('dueDate')
    
    current_user = token_auth.current_user()
    
    new_task = Task(title=title, description=description, completed=completed, dueDate=dueDate,user_id=current_user.id)
    
    return new_task.to_dict(), 201

# Update Task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def edit_task(task_id):
    # Check to see that they have a JSON body
    if not request.is_json:
        return {'error': 'Content-type must be application/json'}, 400
    # Find the task in the db
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f"Task with ID #{task_id} does not exist"}, 404
    # Get the current user based on the token
    current_user = token_auth.current_user()
    # Check if the current user is the author of the task
    if current_user is not task.author:
        return {'error': "This is not your task. You do not have permission to edit"}, 403
    
    # Get the data from the request
    data = request.json
    # Pass that data into the task's update method
    task.update(**data)
    return task.to_dict()

# Update User
@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def edit_user(user_id):
    # Check to see that they have a JSON body
    if not request.is_json:
        return {'error': 'Content-type must be application/json'}, 400
    # Find the user in the db
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f"User with ID #{user_id} does not exist"}, 404
    # Get the current user based on the token
    current_user = token_auth.current_user()
    # Check if the current user is the user editing
    if current_user is not user:
        return {'error': "Not authorized to edit this user!"}, 403
    
    # Get the data from the request
    data = request.json
    # Pass that data into the task's update method
    user.update(**data)
    return user.to_dict()

#Delete a Task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_auth.login_required
def delete_task(task_id):
    # based on task_id parameter check to see Task exists
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f'Task with {task_id} does not exist. Please try again'}, 404
    #Ensure user trying to delete task is authorized
    current_user = token_auth.current_user()
    if task.author is not current_user:
        return {'error': 'You do not have permission to delete this task'}, 403
    #Delete the task
    task.delete()
    return {'success': f"{task.title} was successfully deleted"}, 200

#Delete a User
@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    # based on user_id parameter check to see User exists
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f'User with ID #{user_id} does not exist. Please try again'}, 404
    #Ensure user trying to delete user is authorized
    current_user = token_auth.current_user()
    if user is not current_user:
        return {'error': 'Not authorized to delete this user!'}, 403
    #Delete the user
    user.delete()
    return {'success': f"{user.username} was successfully deleted"}, 200