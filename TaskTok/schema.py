from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.String()
    username = fields.String()
    email = fields.String()


class TaskSchema(Schema):
    id = fields.String()
    owner_username = fields.String()
    task_emailList = fields.String()
    task_reminderOffSetTime = fields.DateTime()
    task_dueDate = fields.DateTime()
    task_description = fields.String()
    task_name = fields.String()
    task_message = fields.String()
