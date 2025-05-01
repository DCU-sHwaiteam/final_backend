from flask import Blueprint, request, jsonify, session
from app import db
from app.models.clubmembership import ClubMembership
from app.models.club import Club
from app.models.user import User
import logging
# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 콘솔 출력 핸들러 추가
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
bp = Blueprint('clubmembership', __name__)

# 한글 응답용 JSON 함수
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

# 동아리 가입 요청 API (POST)
@bp.route('/api/join-club', methods=['POST'])
def join_club():
    data = request.get_json()
    logger.info("[join_club] 수신 데이터:", data)
    user_id = data.get('user_id')
    club_id = data.get('club_id')
    logger.info("user_id:", user_id, "club_id:", club_id)
    # 회원과 동아리 존재 여부 확인
    user = User.query.get(user_id)
    club = Club.query.get(club_id)
    logger.info("user 존재 여부:", bool(user))
    logger.info("club 존재 여부:", bool(club))

    if not user or not club:
        logger.info("존재하지 않는 user 또는 club")
        return json_response({"success": False, "message": "회원 또는 동아리가 존재하지 않습니다."}, 404)

    # 이미 가입된 회원인지 확인
    existing_membership = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
    logger.info("기존 가입 여부:", bool(existing_membership))
    if existing_membership:
         return json_response({"success": False, "message": "이미 가입된 회원입니다."}, 409)

    # 가입 요청 생성
    membership = ClubMembership(user_id=user_id, club_id=club_id)
    db.session.add(membership)
    db.session.commit()
    logger.info("가입 성공:", membership.to_dict())
    return json_response({"success": True, "membership": membership.to_dict()}, 201)

# 동아리장 승인 API (POST)
@bp.route('/api/approve-membership', methods=['POST'])
def approve_membership():
    data = request.get_json()
    logger.info("[approve_membership] 수신 데이터:", data)
    user_id = data.get('user_id')
    club_id = data.get('club_id')

    # 동아리장 이메일 확인
    club = Club.query.get(club_id)
    logger.info("동아리 존재 여부:", bool(club))
    if not club:
        return json_response({"success": False, "message": "동아리를 찾을 수 없습니다."}, 404)
    logger.info("실제 동아리장:", club.leader_email)
    logger.info("요청자 이메일:", leader_email)

    # 동아리장만 승인 가능
    if club.leader_email != data.get('leader_email'):
        return json_response({"success": False, "message": "동아리장만 승인할 수 있습니다."}, 403)

    # 해당 회원의 가입 요청 상태가 'pending'인지 확인
    membership = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
    logger.info("가입 요청 존재 여부:", bool(membership))
    if not membership:
         return json_response({"success": False, "message": "가입 요청을 찾을 수 없습니다."}, 404)

    # 상태 변경: 'approved'로 승인
    membership.status = 'approved'
    db.session.commit()
    logger.info("승인 완료:", membership.to_dict())
    return json_response({"success": True, "membership": membership.to_dict()})

# 동아리 가입 신청자 목록 조회
@bp.route('/api/clubs/<int:club_id>/applications', methods=['GET'])
def get_applications(club_id):
    applications = ClubMembership.query.filter_by(club_id=club_id, status='pending').all()
    users = [User.query.get(a.user_id).to_dict() for a in applications]
    return jsonify(users), 200

# 동아리 멤버 목록 조회
@bp.route('/api/clubs/<int:club_id>/members', methods=['GET'])
def get_club_members(club_id):
    memberships = ClubMembership.query.filter_by(club_id=club_id, status='approved').all()
    users = [User.query.get(m.user_id).to_dict() for m in memberships]
    return jsonify(users), 200

# 동아리 멤버 삭제
@bp.route('/api/clubs/<int:club_id>/members/<int:user_id>', methods=['DELETE'])
def remove_member(club_id, user_id):
    membership = ClubMembership.query.filter_by(club_id=club_id, user_id=user_id).first()
    if not membership:
        return jsonify({'success': False, 'message': '해당 멤버가 없습니다.'}), 404
    db.session.delete(membership)
    db.session.commit()
    return jsonify({'success': True})

