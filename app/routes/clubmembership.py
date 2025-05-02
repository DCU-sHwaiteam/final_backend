from flask import Blueprint, request, jsonify, session
from app import db
from app.models.clubmembership import ClubMembership
from app.models.club import Club
from app.models.user import User
import logging

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

bp = Blueprint('clubmembership', __name__)

def json_response(data, status=200):
    from flask import make_response
    import json
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, status

@bp.route('/api/my-clubs', methods=['GET'])
def get_my_clubs():
    user_id = session.get('user_id')
    logger.info(f"[my-clubs] 현재 요청한 user_id: {user_id}")
    if not user_id:
        return json_response({"success": False, "message": "로그인이 필요합니다."}, 401)

    memberships = ClubMembership.query.filter_by(user_id=user_id, status='approved').all()
    clubs = [membership.club.to_dict() for membership in memberships]
    return json_response(clubs)

@bp.route('/api/join-club', methods=['POST'])
def join_club():
    data = request.get_json()
    logger.info(f"[join_club] 수신 데이터: {data}")
    user_id = data.get('user_id')
    club_id = data.get('club_id')
    logger.info(f"user_id: {user_id}, club_id: {club_id}")
    user = User.query.get(user_id)
    club = Club.query.get(club_id)
    logger.info(f"user 존재 여부: {bool(user)}")
    logger.info(f"club 존재 여부: {bool(club)}")

    if not user or not club:
        logger.info("존재하지 않는 user 또는 club")
        return json_response({"success": False, "message": "회원 또는 동아리가 존재하지 않습니다."}, 404)

    existing_membership = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
    logger.info(f"기존 가입 여부: {bool(existing_membership)}")
    if existing_membership:
         return json_response({"success": False, "message": "이미 가입된 회원입니다."}, 409)

    membership = ClubMembership(user_id=user_id, club_id=club_id)
    db.session.add(membership)
    db.session.commit()
    logger.info(f"가입 성공: {membership.to_dict()}")
    return json_response({"success": True, "membership": membership.to_dict()}, 201)

@bp.route('/api/approve-membership', methods=['POST'])
def approve_membership():
    data = request.get_json()
    logger.info(f"[approve_membership] 수신 데이터: {data}")
    user_id = data.get('user_id')
    club_id = data.get('club_id')

    # 세션에서 현재 사용자 확인
    session_user_id = session.get('user_id')
    if not session_user_id:
        return json_response({"success": False, "message": "로그인이 필요합니다."}, 401)

    session_user = User.query.get(session_user_id)
    if not session_user:
        return json_response({"success": False, "message": "유효하지 않은 사용자입니다."}, 401)

    club = Club.query.get(club_id)
    logger.info(f"동아리 존재 여부: {bool(club)}")
    if not club:
        return json_response({"success": False, "message": "동아리를 찾을 수 없습니다."}, 404)
    logger.info(f"실제 동아리장: {club.leader_email}")
    logger.info(f"요청자 이메일: {session_user.email}")

    # 동아리장만 승인 가능 (세션 사용자의 이메일과 비교)
    if club.leader_email != session_user.email:
        return json_response({"success": False, "message": "동아리장만 승인할 수 있습니다."}, 403)

    membership = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
    logger.info(f"가입 요청 존재 여부: {bool(membership)}")
    if not membership:
         return json_response({"success": False, "message": "가입 요청을 찾을 수 없습니다."}, 404)

    try:
        membership.status = 'approved'
        db.session.commit()
        logger.info(f"승인 완료: {membership.to_dict()}")
        return json_response({"success": True, "membership": membership.to_dict()})
    except Exception as e:
        db.session.rollback()
        logger.error(f"승인 실패: {str(e)}")
        return json_response({"success": False, "message": "서버 오류 발생"}, 500)

@bp.route('/api/clubs/<int:club_id>/applications', methods=['GET'])
def get_applications(club_id):
    applications = ClubMembership.query.filter_by(club_id=club_id, status='pending').all()
    users = [User.query.get(a.user_id).to_dict() for a in applications]
    return jsonify(users), 200

@bp.route('/api/clubs/<int:club_id>/members', methods=['GET'])
def get_club_members(club_id):
    memberships = ClubMembership.query.filter_by(club_id=club_id, status='approved').all()
    users = [User.query.get(m.user_id).to_dict() for m in memberships]
    return jsonify(users), 200

@bp.route('/api/clubs/<int:club_id>/members/<int:user_id>', methods=['DELETE'])
def remove_member(club_id, user_id):
    membership = ClubMembership.query.filter_by(club_id=club_id, user_id=user_id).first()
    if not membership:
        return jsonify({'success': False, 'message': '해당 멤버가 없습니다.'}), 404
    db.session.delete(membership)
    db.session.commit()
    return jsonify({'success': True})


