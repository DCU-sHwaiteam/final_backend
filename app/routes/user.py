from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from flask import current_app
from flask import session

bp = Blueprint('user', __name__, url_prefix='/api')

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json

        required_fields = ['email', 'name', 'student_id', 'department', 'phone', 'password']
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({'success': False, 'message': '모든 필드를 입력해주세요.'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': '이미 존재하는 이메일입니다.'}), 409

        if User.query.filter_by(student_id=data['student_id']).first():
            return jsonify({'success': False, 'message': '이미 존재하는 학번입니다.'}), 409

        user = User(
            email=data['email'],
            name=data['name'],
            student_id=data['student_id'],
            department=data['department'],  
            phone=data['phone'],
            password=generate_password_hash(data['password'])
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({'success': True, 'message': '회원가입 성공'}), 201

    except Exception as e:
        print("[회원가입 실패]", e)
        return jsonify({'success': False, 'message': '서버 오류가 발생했습니다.'}), 500


@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({"message": "아이디와 비밀번호를 입력해주세요."}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401

        session['user_id'] = user.id
        session['user_email'] = user.email
        return jsonify({"message": "로그인 성공!"}), 200

    except Exception as e:
        print("[로그인 실패]", e)
        return jsonify({"message": "서버 오류가 발생했습니다."}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "로그아웃 완료!"}), 200


#  로그인한 사용자 정보 조회
@bp.route('/current-user', methods=['GET'])
def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    user = User.query.get(user_id)
    return jsonify({'success': True, 'user': user.to_dict()})

