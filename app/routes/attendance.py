from flask import Blueprint, request, jsonify, session
from app.models.attendance import Attendance
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import and_
from functools import wraps

bp = Blueprint('attendance', __name__, url_prefix='/api')

#세션 기반 인증 데코레이터
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': '로그인이 필요합니다.'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '사용자를 찾을 수 없습니다.'}), 404
        return f(user, *args, **kwargs)
    return decorated

@bp.route('/attendance', methods=['POST'])
@login_required
def record_attendance(current_user):
    data = request.json
    club_id = data.get('club_id')
    input_password = data.get('attendance_password')
    status = data.get('status', '출석')  # 기본값

    if not club_id or not input_password:
        return jsonify({'message': '동아리 ID와 출석 비밀번호가 필요합니다.'}), 400

    club = Club.query.get(club_id)
    if not club:
        return jsonify({'message': '해당 동아리가 존재하지 않습니다.'}), 404

    if club.attendance_password != input_password:
        return jsonify({'message': '출석 비밀번호가 틀립니다.'}), 403

    today = datetime.utcnow().date()
    existing = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.club_id == club_id,
        db.func.date(Attendance.timestamp) == today
    ).first()

    if existing:
        return jsonify({'message': '오늘은 이미 출석했습니다.'}), 409

    new_record = Attendance(
        user_id=current_user.id,
        club_id=club_id,
        status=status,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_record)
    db.session.commit()

    return jsonify({'message': '출석 등록 완료!', 'status': status}), 201


# 본인 출석 목록 조회
@bp.route('/attendance/history', methods=['GET'])
@login_required
def attendance_history(current_user):
    records = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.timestamp.desc()).all()

    history = [
        {
            'date': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': record.status
        }
        for record in records
    ]

    return jsonify({'attendance': history}), 200

# 관리자 전체 출석 기록 조회
@bp.route('/admin/attendance/all', methods=['GET'])
@login_required
def admin_attendance_all(current_user):
    if current_user.email != 'admin@admin.com':
        return jsonify({'message': '관리자 권한이 없습니다.'}), 403

    records = Attendance.query.order_by(Attendance.timestamp.desc()).all()

    all_data = [
        {
            'user_id': record.user_id,
            'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': record.status
        }
        for record in records
    ]

    return jsonify({'attendance': all_data}), 200

@bp.route('/clubs/<int:club_id>/attendance-password', methods=['PATCH'])
@login_required
def update_attendance_password(club_id):
    data = request.json
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({'message': '새 출석 비밀번호를 입력해주세요.'}), 400

    club = Club.query.get(club_id)
    if not club:
        return jsonify({'message': '해당 동아리를 찾을 수 없습니다.'}), 404

    if club.leader_email != current_user.email:
        return jsonify({'message': '출석 비밀번호를 수정할 권한이 없습니다.'}), 403

    club.attendance_password = new_password
    db.session.commit()

    return jsonify({'message': '출석 비밀번호가 수정되었습니다.'}), 200
