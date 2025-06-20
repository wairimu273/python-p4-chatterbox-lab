from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Message
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.to_dict() for message in messages])
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('body') or not data.get('username'):
            return jsonify({'error': 'Body and username are required'}), 400
        message = Message(body=data['body'], username=data['username'])
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get_or_404(id)
    
    if request.method == 'PATCH':
        data = request.get_json()
        if not data or 'body' not in data:
            return jsonify({'error': 'Body is required'}), 400
        message.body = data['body']
        message.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(message.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return jsonify({}), 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)