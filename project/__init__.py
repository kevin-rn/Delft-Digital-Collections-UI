import os

from flask import Flask

from project.config import config


# instantiate extensions here if we have them



def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")

    # instantiate the app
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])

    # set up extensions here when we have them
    
    # register blueprints
    from project.errors import errors_blueprint
    app.register_blueprint(errors_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app}

    return app