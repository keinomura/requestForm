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
    __tablename__ = 'Requests'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    requester_department = db.Column(db.String(255))
    requester_name = db.Column(db.String(255))
    input_date = db.Column(db.DateTime, default=db.func.current_timestamp())

class Response(db.Model):
    __tablename__ = 'Responses'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('Requests.id'))
    handler_company = db.Column(db.String(255))
    handler_department = db.Column(db.String(255))
    handler_name = db.Column(db.String(255))
    status = db.Column(db.String(50), default='未対応')
    response_comment = db.Column(db.Text)
    final_response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    final_response_date = db.Column(db.DateTime)

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
    if 'requester_department' not in data:
        return jsonify({'error': 'requester_department is required'}), 400
    new_request = Request(
        content=data['content'],
        requester_department=data['requester_department'],
        requester_name=data['requester_name']
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': '新しい要望が追加されました'}), 201

@app.route('/requests', methods=['GET'])
def get_requests():
    requests = Request.query.all()
    output = []
    for req in requests:
        output.append({
            'id': req.id,
            'content': req.content,
            'requester_department': req.requester_department,
            'requester_name': req.requester_name,
            'input_date': req.input_date
        })
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
