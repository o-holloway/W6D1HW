from app import app, db
from flask import request
from .models import Task

#Define route
@app.route('/')
def index():
    return 'Task API'

#Return all tasks as JSON object
@app.route('/tasks')
def get_tasks():
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where((Task.title.ilike(f"%{search}%")) | (Task.body.ilike(f"%{search}%"))) #searches in title or body
    # Get the tasks from the database
    tasks = db.session.execute(select_stmt).scalars().all()
    return [p.to_dict() for p in tasks]

#Get a single task by ID
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    # Get the task from the database by ID
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"Task with an ID of {task_id} does not exist"}, 404

#Create a task
@app.route('/tasks', methods=['POST'])
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
    createdAt = '2024-03-25T15:21:35'
    dueDate = data.get('dueDate')
    
    new_post = Task(title=title, description=description, completed=completed, createdAt=createdAt, dueDate=dueDate, id=3)
    
    return new_post.to_dict(), 201