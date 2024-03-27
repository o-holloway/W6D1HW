from app import app
from fake_data.tasks import tasks_list
from flask import request

tasks = []

#Define route
@app.route('/')
def index():
    return 'Task API'

#Get all tasks as JSON object
@app.route('/tasks')
def get_tasks():
    tasks = tasks_list
    return tasks

#Get a single task by ID
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    tasks = tasks_list
    for task in tasks:
        if task['id'] == task_id:
            return task
    return {'error': f"Task with an ID of {task_id} does not exist"},404

#Create a task
@app.route('/tasks', methods=['POST'])
def  create_task():
    if not request.is_json:
        return {'error': f"Content-type must be application/json"},400
    data = request.json
    required_fields = ['title', 'description', 'dueDate']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    title = data.get('title')
    description = data.get('description')
    completed = False
    createdAt = '2024-03-25T15:21:35'
    dueDate = data.get('dueDate')
        
    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "description": description,
        "completed": completed,
        "createdAt": createdAt,
        "dueDate": dueDate
    }
    tasks.append(new_task)

    return new_task, 201