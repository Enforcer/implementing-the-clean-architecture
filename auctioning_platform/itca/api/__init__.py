from flask import Flask
from flask_injector import FlaskInjector

from itca.api.auctions import AuctionsApi
from itca.api.auctions.blueprint import auctions_blueprint
from itca.main import assemble


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(auctions_blueprint, url_prefix="/auctions")

    FlaskInjector(
        app,
        modules=[AuctionsApi()],
        injector=assemble(),
    )

    return app
