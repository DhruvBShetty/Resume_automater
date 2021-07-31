import os

from flask import Flask
from flaskr import db
from flaskr import auth
from flaskr import blog  
from flask import flash, request, redirect, url_for,render_template
from werkzeug.utils import secure_filename
from zipfile import ZipFile



def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    ALLOWED_EXTENSIONS = {'txt', 'pdf','doc','docx'}
    UPLOAD_FOLDER="/home/dhruv/Desktop/instance/uploads"
    app = Flask(__name__, instance_relative_config=True)
   
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite")
        
    )
    
    
   

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Hello, World!"
    
    db.init_app(app)
    
    app.register_blueprint(auth.bp)
    
    app.register_blueprint(blog.bp)
    
    app.add_url_rule('/', endpoint='index')
    
    
    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route("/uploaded", methods=['GET', 'POST'])
    def upload_file():
        if request.method == "POST":
            
            file = request.files["file"]

            if request.files:
               if file.filename == '':
                   flash('No selected file')
                   return redirect(request.url)
               
               
               
               file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
               
               if file.filename.rsplit('.', 1)[1].lower()=="zip":
                   with ZipFile(os.path.join(app.config["UPLOAD_FOLDER"], file.filename),"r") as zip_ref:
                        zip_ref.extractall(app.config["UPLOAD_FOLDER"])
               
                   

            print(file)
          
        return redirect(url_for('blog.index'))
    


    return app