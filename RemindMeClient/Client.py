from TaskTok.Server import create_app

app = create_app()
print(app.extensions)
celery = app.extensions["celery"]