from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 全てのオリジンを許可

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# モデルの定義
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(200), nullable=False)

# データベースの初期化（初回のみ必要）
with app.app_context():
    db.create_all()

# テストデータの追加（必要に応じて）
with app.app_context():
    if Request.query.count() == 0:
        test_request = Request(requester_name="山田太郎", content="新しい機能を追加してください")
        db.session.add(test_request)
        db.session.commit()

@app.route('/requests', methods=['POST'])
def add_request():
    data = request.get_json()
    new_request = Request(
        requester_name=data['requester_name'],
        content=data['content']
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': '新しい要望が追加されました', 'request': data}), 201

@app.route('/requests', methods=['GET'])
def get_requests():
    requests = Request.query.all()
    result = [
        {'id': req.id, 'requester_name': req.requester_name, 'content': req.content}
        for req in requests
    ]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
