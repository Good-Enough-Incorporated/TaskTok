#from TaskTok import create_app
from TaskTok.extensions import celery_worker as celery

# create our Flask app, so we can get the app.config properties.
# app = create_app()


#app = create_app()
#celery_worker = app.celery_app

#celery = celery_app.extensions['celery']

# When we call our worker
# celery -A RemindMeClient.Client.celery object
# we're referencing this little guy below
# celery = app.extensions["celery"]
