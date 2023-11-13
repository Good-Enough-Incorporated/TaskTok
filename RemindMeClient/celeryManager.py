from celery import Celery, Task
from flask import Flask
import functools
from threading import RLock
import kombu.utils
#bug with python 3.12 and celery
#https://github.com/celery/kombu/issues/1804
if not getattr(kombu.utils.cached_property, 'lock', None):
    setattr(kombu.utils.cached_property, 'lock', functools.cached_property(lambda _: RLock()))
    # Must call __set_name__ here since this cached property is not defined in the context of a class
    # Refer to https://docs.python.org/3/reference/datamodel.html#object.__set_name__
    kombu.utils.cached_property.lock.__set_name__(kombu.utils.cached_property, 'lock')

def celery_init_app(app):
    celery = Celery(
        app.import_name,
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
#    class FlaskTask(Task):
#        def __call__(self, *args: object, **kwargs: object) -> object:
#            with app.app_context():
#                return self.run(*args, **kwargs)
#
#    celery_app = Celery(app.name)
#    celery_app.config_from_object(app.config["CELERY"])
#    celery_app.Task = FlaskTask
#    celery_app.set_default()
#    app.extensions["celery"] = celery_app
#    return celery_app