import pytest
from flask import Flask
from flask_cors import CORS

@pytest.fixture
def app():
    app = Flask(__name__)
    CORS(app)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner() 