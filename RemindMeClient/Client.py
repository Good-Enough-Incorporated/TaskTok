#from TaskTok import create_app
from TaskTok.extensions import celery_worker as celery
from dotenv import load_dotenv
import os
# create our Flask app, so we can get the app.config properties.
# app = create_app()


#app = create_app()
#celery_worker = app.celery_app
load_dotenv()
celery.conf.broker_url = os.environ.get('broker_url') #celery doesn't like the CELERY_ prefix.
celery.conf.result_backend = os.environ.get('result_backend') #celery doesn't like the CELERY_ prefix.
#app.config['result_backend'] = os.environ.get('result_backend') #celery doesn't like the CELERY_ prefix.

#celery = celery_app.extensions['celery']

# When we call our worker
# celery -A RemindMeClient.Client.celery object
# we're referencing this little guy below
# celery = app.extensions["celery"]
