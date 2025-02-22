import os
from flask import Flask
from routes.create_cv import create_cv
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(create_cv)

if __name__ == '__main__':
    app.run(host='localhost', port=3000)