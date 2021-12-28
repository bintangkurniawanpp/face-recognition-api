from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from db import db
from config import Config

from resources.predict import Predict

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)



api.add_resource(Predict, '/predict')

if __name__ == '__main__':
    app.run(port=5000, debug=True)