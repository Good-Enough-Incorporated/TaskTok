from setuptools import setup

setup(
    name='reminder_client',
    version='0.1',
    packages=['RemindMeClient'],
    include_package_data=True,
    install_requires=[
        'Flask-SQLAlchemy',
        'Celery',
    ],
)
