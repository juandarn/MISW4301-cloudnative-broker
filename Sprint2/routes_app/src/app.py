import os
from flask import Flask, jsonify, Response
from db import engine, SessionLocal
from models.route import Base, Route
from resources.route import bp as routes_bp


def create_app():
    app = Flask(__name__)

    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    # Reset global: disponible en /reset y /routes/reset (exige BD limpia)
    @app.post("/routes/reset")
    def reset_db():
        db = SessionLocal()
        try:
            db.query(Route).delete()
            db.commit()
            return jsonify({"msg": "Todos los datos fueron eliminados"})
        finally:
            db.close()

    # Registrar recursos de /routes
    app.register_blueprint(routes_bp, url_prefix="/routes")

    # Liberar sesiones por request (si usas scoped_session, cambia por remove)
    @app.teardown_appcontext
    def cleanup(_exc=None):
        try:
            SessionLocal.remove()  # si es scoped_session
        except Exception:
            pass

    return app


# Ejecución local:
# python -m flask --app app:create_app run -h 0.0.0.0 -p 8000
