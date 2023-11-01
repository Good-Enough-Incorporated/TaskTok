from TaskTok.Server import create_app
from TaskTok import app
#create our Flask app so we can get the app.config properties.
#app = create_app()
with app.app_context():
    celery = app.extensions["celery"]
#When we call our worker
#celery -A RemindMeClient.Client.celery object 
#we're referencing this little guy below
#celery = app.extensions["celery"]