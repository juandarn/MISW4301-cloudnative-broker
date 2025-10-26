from flask import Flask
from flask_smorest import Api
import os

from db import db
import models
from resources.post import blp as post_blp
from dotenv import load_dotenv

load_dotenv()

# Patrón de fábrica
def create_app(db_url=None):
    app = Flask(__name__)

    # Sirve para propagar excepciones dentro de la aplicación
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Posts REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # Configurar base de datos - usar PostgreSQL en producción, SQLite para desarrollo
    database_uri = os.getenv("DATABASE_URI")
    if database_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    else:
        # Fallback para desarrollo local
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    api = Api(app)

    with app.app_context():
        db.create_all()

    api.register_blueprint(post_blp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
