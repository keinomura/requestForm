from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # 全てのオリジンを許可
# CORS(app)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///request_management.db'
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
    status = db.Column(db.String(50), default='未対応')
    response_comment = db.Column(db.Text)
    assigned_department = db.Column(db.String(255))
    assigned_person = db.Column(db.String(255))
    update_date = db.Column(db.DateTime)

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

@app.route('/responses', methods=['POST'])
def add_response():
    data = request.get_json()
    
    # 日付の変換
    response_date = datetime.fromisoformat(data['response_date']) if 'response_date' in data else None
    final_response_date = datetime.fromisoformat(data['final_response_date']) if 'final_response_date' in data else None
    
    new_response = Response(
        request_id=data['request_id'],
        handler_company=data.get('handler_company', ''),
        handler_department=data.get('handler_department', ''),
        handler_name=data.get('handler_name', ''),
        status=data.get('status', '未対応'),
        response_comment=data.get('response_comment', ''),
        final_response=data.get('final_response', ''),
        response_date=response_date,
        final_response_date=final_response_date
    )
    db.session.add(new_response)
    db.session.commit()
    return jsonify({'message': '新しい対応が追加されました'}), 201

# 要望一覧の取得API
@app.route('/requests', methods=['GET'])
def get_requests():
    requests = Request.query.all()
    output = []
    for request_item in requests:
        output.append({
            'id': request_item.id,
            'content': request_item.content,
            'requester_department': request_item.requester_department,
            'requester_name': request_item.requester_name,
            'input_date': request_item.input_date,
            'status': request_item.status,
            'response_comment': request_item.response_comment,
            'assigned_department': request_item.assigned_department,
            'assigned_person': request_item.assigned_person,
            'update_date': request_item.update_date
        })
    return jsonify(output)

# 進捗情報の取得API :FIXME 要らないかも
@app.route('/responses/<int:response_id>', methods=['PUT'])
def update_response(response_id):
    data = request.get_json()
    response = Response.query.get(response_id)
    if response is None:
        return jsonify({'error': '指定された進捗情報が見つかりませんでした'}), 404
    
    # 更新内容
    response.handler_company = data.get('handler_company', response.handler_company)
    response.handler_department = data.get('handler_department', response.handler_department)
    response.handler_name = data.get('handler_name', response.handler_name)
    response.status = data.get('status', response.status)
    response.response_comment = data.get('response_comment', response.response_comment)
    response.final_response = data.get('final_response', response.final_response)
    response.response_date = data.get('response_date', response.response_date)
    response.final_response_date = data.get('final_response_date', response.final_response_date)

# 進捗情報の更新API
@app.route('/requests/<int:id>', methods=['PUT'])
def update_request(id):
    data = request.json
    request_item = Request.query.get(id)
    if not request_item:
        return jsonify({"error": "Request not found"}), 404

    request_item.status = data.get('status', request_item.status)
    request_item.response_comment = data.get('response_comment', request_item.response_comment)
    request_item.assigned_department = data.get('assigned_department', request_item.assigned_department)
    request_item.assigned_person = data.get('assigned_person', request_item.assigned_person)
    request_item.update_date = datetime.now()

    db.session.commit()
    return jsonify({"message": "Request updated successfully"})


    # db.session.commit()
    # return jsonify({'message': '進捗情報が更新されました'})


if __name__ == '__main__':
    app.run(debug=True)
