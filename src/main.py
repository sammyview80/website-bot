import os
from flask import Flask
from flask_session import Session
from config import ApplicationConfig
from dotenv import load_dotenv
from models import db
from routes.auth.index import auth
from routes.llm.index import llm

load_dotenv()

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

server_session = Session(app)

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(llm, url_prefix='/llm')

if __name__ == '__main__':
    app.run(debug=False, port=os.environ.get('PORT', 5000))

