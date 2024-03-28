from . import db
from datetime import datetime, timezone, timedelta

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(timezone.utc))
    dueDate = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(timezone.utc) + timedelta(days=+1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Title {self.id}|{self.title}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "createdAt": self.createdAt,
            "dueDate": self.dueDate
        }