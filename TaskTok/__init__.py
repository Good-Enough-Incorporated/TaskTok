from .Server import create_app

#TODO: when uncommented, celery doesn't load its configs
#if __name__ == '__main__':
app = create_app()
