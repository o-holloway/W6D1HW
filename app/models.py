import secrets
from . import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    tasks = db.relationship('Task', back_populates='author')
    token = db.Column(db.String, index=True, unique=True)
    token_expiration = db.Column(db.DateTime(timezone=True))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)
        self.save()

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "dateCreated": self.date_created
        }
        
    def update(self, **kwargs):
        allowed_fields = {'email', 'username', 'password'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()
    
    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return {"token": self.token, "tokenExpiration": self.token_expiration}
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExpiration": self.token_expiration}


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(timezone.utc))
    dueDate = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(timezone.utc) + timedelta(days=+1))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='tasks')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Title {self.id}|{self.title}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "createdAt": self.createdAt,
            "dueDate": self.dueDate,
            "author": self.author.to_dict()
        }
        
    def update(self, **kwargs):
        allowed_fields = {'title', 'description', 'dueDate'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()