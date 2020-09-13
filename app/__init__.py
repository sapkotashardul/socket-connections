from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_socketio import emit


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
socketio = SocketIO(app)
# migrate = Migrate(app, db)

socketio.run(app)

from app import routes, models

