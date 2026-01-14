from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import api

app = Flask(__name__)
CORS(app)

# 注册路由
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)