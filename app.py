import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # 全てのオリジンを許可
# CORS(app)
CORS(app)

# プロジェクトディレクトリに対する相対パスを使用してデータベースファイルのパスを設定
db_path = os.path.join(os.path.dirname(__file__), '.', 'request_management.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# モデルの定義
# 要望についての情報を格納するRequestテーブルと、対応についての情報を格納するResponseテーブルを定義
class Request(db.Model): # 要望についての情報を格納するRequestテーブル
    __tablename__ = 'Requests'
    request_uuid = db.Column(db.String, primary_key=True)  # UUIDを使用するためにString型に変更
    request_id = db.Column(db.Integer, autoincrement=True)  # 表示用のインクリメントID
    content = db.Column(db.Text, nullable=False)
    requester_department = db.Column(db.String(255))
    requester_name = db.Column(db.String(255))
    input_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default='未対応')
    response_comment = db.Column(db.Text)
    assigned_department = db.Column(db.String(255))
    assigned_person = db.Column(db.String(255))
    update_date = db.Column(db.DateTime, default=db.func.current_timestamp())

class Response(db.Model): # 対応についての情報を格納するResponseテーブル
    __tablename__ = 'Responses'
    response_uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))  # UUIDを使用するためにString型に変更
    response_id = db.Column(db.Integer,  autoincrement=True, nullable=True) # 自動インクリメントに設定
    request_uuid = db.Column(db.String, db.ForeignKey('Requests.request_uuid'))  # UUIDを使用するためにString型に変更
    handler_company = db.Column(db.String(255))
    handler_department = db.Column(db.String(255))
    handler_name = db.Column(db.String(255))
    status = db.Column(db.String(50), default='未対応')
    response_comment = db.Column(db.Text)
    final_response = db.Column(db.Text)
    response_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    final_response_date = db.Column(db.DateTime)

# データベースの初期化（初回のみ必要）
with app.app_context():
    db.create_all()

# # テストデータの追加（必要に応じて）
# with app.app_context():
#     if Request.query.count() == 0:
#         test_request = Request(requester_name="山田太郎", content="新しい機能を追加してください")
#         db.session.add(test_request)
#         db.session.commit()

# 新しい要望を追加するAPI
@app.route('/requests', methods=['POST'])
def add_request():
    data = request.get_json()
    if 'requester_department' not in data:
        return jsonify({'error': 'requester_department is required'}), 400
    new_request = Request(
        request_uuid=data['request_uuid'],
        content=data['content'],
        requester_department=data['requester_department'],
        requester_name=data['requester_name']
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': '新しい要望が追加されました'}), 201

# 新しい対応を追加するAPI
@app.route('/responses', methods=['POST'])
def add_response():
    data = request.get_json()
    
    # 日付の変換
    response_date = datetime.fromisoformat(data['response_date']) if 'response_date' in data else None
    final_response_date = datetime.fromisoformat(data['final_response_date']) if 'final_response_date' in data else None
    
    new_response = Response(
        request_uuid=data['request_uuid'],
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
            'request_uuid': request_item.request_uuid,
            'request_id': request_item.request_id,
            'content': request_item.content,
            'requester_department': request_item.requester_department,
            'requester_name': request_item.requester_name,
            'input_date': request_item.input_date,
            'status': request_item.status,
            'response_comment': request_item.response_comment,
            'assigned_department': request_item.assigned_department,
            'assigned_person': request_item.assigned_person,
            # 'update_date': (request_item.update_date).strftime('%Y-%m-%d %H:%M:%S') if request_item.update_date else None  # 日本時間に変換
            'update_date': request_item.update_date if request_item.update_date else None  # 日本時間に変換しない。 input_dataと同じ形式で返す

        })
    return jsonify(output)

# 進捗情報の更新API　
@app.route('/requests/<request_uuid>', methods=['PUT'])
def update_request(request_uuid):
    data = request.json
    request_item = Request.query.filter_by(request_uuid=request_uuid).first()
    if not request_item:
        return jsonify({"error": "Request not found"}), 404

    # Requestテーブルの更新
    request_item.status = data.get('status', request_item.status)
    request_item.response_comment = data.get('response_comment', request_item.response_comment)
    request_item.assigned_department = data.get('assigned_department', request_item.assigned_department)
    request_item.assigned_person = data.get('assigned_person', request_item.assigned_person)
    request_item.update_date = datetime.utcnow()

    # デバッグ用のログを追加
    print(f"Updated request_item.update_date: {request_item.update_date}")

    # Responseテーブルに新しいコメントを追加
    new_response = Response(
        request_uuid=request_uuid,
        handler_department=data.get('assigned_department', ''),
        handler_name=data.get('assigned_person', ''),
        status=data.get('status', '未対応'),
        response_comment=data.get('response_comment', ''),
        response_date=datetime.utcnow()
    )
    db.session.add(new_response)
    db.session.commit()
    return jsonify({"message": "Request updated successfully"})


# 特定のリクエストに関連するコメントを取得するAPI
@app.route('/requests/<request_uuid>/comments', methods=['GET'])
def get_request_comments(request_uuid):
    request_item = Request.query.filter_by(request_uuid=request_uuid).first()
    if not request_item:
        return jsonify({"error": "Request not found"}), 404

    responses = Response.query.filter_by(request_uuid=request_uuid).all()
    comments = []
    for response in responses:
        comments.append({
            'response_uuid': response.response_uuid,
            'handler_department': response.handler_department,
            'handler_name': response.handler_name,
            'status': response.status,
            'response_comment': response.response_comment,
            'response_date': response.response_date
        })
        print('res', response.response_date.time())
    return jsonify(comments)

#リクエストの削除API
@app.route('/requests/<request_uuid>', methods=['DELETE'])
def delete_request(request_uuid):
    request_item = Request.query.get(request_uuid)
    if not request_item:
        return jsonify({"error": "Request not found"}), 404

    db.session.delete(request_item)
    db.session.commit()
    return jsonify({"message": "Request deleted successfully"}), 200

# コメントの削除API
@app.route('/comments/<response_uuid>', methods=['DELETE'])
def delete_comment(response_uuid):
    comment = Response.query.filter_by(response_uuid=response_uuid).first()
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
