from flask import Flask, app
from flask_smorest import Api
import os

from db import db
import models
from resources.offer import blp as user_blp
from dotenv import load_dotenv

load_dotenv()

#Patrón de fabrica
def create_app(db_url=None):
    app = Flask(__name__)

    # Sirve para propagar excepciones dentro de la aplicación
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "offer REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    
    db.init_app(app)

    api = Api(app)

    with app.app_context():
        db.create_all()

    api.register_blueprint(user_blp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)