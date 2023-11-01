from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery_config = {k.lower().replace('celery_', ''): v for k, v in app.config.items() if 'CELERY_' in k}
    celery.conf.update(celery_config)
    return celery
