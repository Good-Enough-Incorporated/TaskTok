"""
This module, `schema.py`, defines Marshmallow schemas for serialization and deserialization
of data models. It includes schemas for different models like User and Task, providing a 
structured and validated way to convert these models to and from various formats, such as
JSON. Each schema class defines the fields and their data types for the respective model,
 ensuring data integrity during the serialization and deserialization process.
"""
from marshmallow import fields, Schema


class UserSchema(Schema):
    """
    Schema for serializing and deserializing User data. It defines the structure and data types of the User model for easy conversion to and from JSON or other formats.
    
    Fields:
    - id: A String field representing the user's unique identifier.
    - username: A String field representing the user's username.
    - email: A String field representing the user's email address.
    """
    id = fields.String()
    username = fields.String()
    email = fields.String()


class TaskSchema(Schema):
    """
    Schema for serializing and deserializing Task data. It defines the structure and data types of the Task model for easy conversion to and from JSON or other formats.
    
    Fields:
    - id: A String field representing the task's unique identifier.
    - owner_username: A String field representing the username of the task owner.
    - task_emailList: A String field representing the list of emails associated with the task.
    - task_reminderOffSetTime: A DateTime field representing the offset time for task reminders.
    - task_dueDate: A DateTime field representing the due date of the task.
    - task_description: A String field representing the description of the task.
    - task_name: A String field representing the name of the task.
    - task_message: A String field representing the message associated with the task.
    """
    id = fields.String()
    owner_username = fields.String()
    task_emailList = fields.String()
    task_reminderOffSetTime = fields.DateTime()
    task_dueDate = fields.DateTime()
    task_description = fields.String()
    task_name = fields.String()
    task_message = fields.String()
