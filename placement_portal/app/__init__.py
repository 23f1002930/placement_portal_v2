import os
from flask import Flask, jsonify, send_from_directory
from config import Config
from .extensions import db

def create_app(config=None):
    app=Flask(__name__,static_folder=None)
    app.config.from_object(config or Config)
    for key in ("UPLOAD_FOLDER","EXPORT_FOLDER","REPORT_FOLDER"):
        os.makedirs(app.config[key],exist_ok=True)
    db.init_app(app)
    from .api import api
    app.register_blueprint(api)
    @app.get("/")
    def index(): return send_from_directory(os.path.join(app.root_path,"..","frontend"),"index.html")
    @app.get("/frontend/<path:name>")
    def frontend(name): return send_from_directory(os.path.join(app.root_path,"..","frontend"),name)
    @app.errorhandler(404)
    def missing(_): return jsonify(success=False,message="Resource not found",errors={}),404
    @app.errorhandler(413)
    def too_large(_): return jsonify(success=False,message="Upload is too large",errors={}),413
    return app

