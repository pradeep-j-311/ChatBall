import os 
from flask import Flask, render_template

def create_app(test_config=None): 
    # create and configure the app 
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', 
        DATABASE=os.path.join(app.instance_path, 'ChatBall_app.data')
    )
    if test_config is None: 
        app.config.from_pyfile('config.py', silent=True)
    else: 
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # a simple page that says hello
    @app.route('/')
    def homePage():
        return render_template('index.html')
    
    from . import process_chat
    process_chat.init_app(app)
    
    return app