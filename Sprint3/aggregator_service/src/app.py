from flask import Flask, jsonify, current_app
from flask_smorest import Api
import os
from resources.aggregator import blp as aggregator_blp
from resources.rf004_offers import blp as rf004_blp
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

load_dotenv()

#Patrón de fabrica
def create_app(db_url=None):
    app = Flask(__name__)

    # Sirve para propagar excepciones dentro de la aplicación
    app.config["PROPAGATE_EXCEPTIONS"] = False
    app.config["TRAP_HTTP_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Aggregator REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    api = Api(app)


    api.register_blueprint(aggregator_blp)
    api.register_blueprint(rf004_blp)

    @app.errorhandler(HTTPException)
    def handle_http_exc(e: HTTPException):
        payload = {"msg": e.description or e.name}
        return jsonify(payload), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e: Exception):
        current_app.logger.exception(e)
        return jsonify({"msg": "El servicio está temporalmente fuera de servicio."}), 503

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)