from flask import Blueprint, request, jsonify
from app import db
from app.models.clubmembership import ClubMembership
from app.models.club import Club
from app.models.user import User

bp = Blueprint('clubmembership', __name__)

# 한글 응답용 JSON 함수
def json_response(data, status=200):
    from flask import make_response
    import json
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, status

# 동아리 가입 요청 API (POST)
@bp.route('/api/join-club', methods=['POST'])
def join_club():
    data = request.get_json()

    user_id = data.get('user_id')
    club_id = data.get('club_id')

    # 회원과 동아리 존재 여부 확인
    user = User.query.get(user_id)
    club = Club.query.get(club_id)

    if not user or not club:
        return json_response({"success": False, "message": "회원 또는 동아리가 존재하지 않습니다."}, 404)

    # 이미 가입된 회원인지 확인
    existing_membership = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
    if existing_membership:
        return json_response({"success": False, "message": "이미 가입된 회원입니다."}, 409)

    # 가입 요청 생성
    membership = ClubMembership(user_id=user_id, club_id=club_id)
    db.session.add(membership)
    db.session.commit()

    return json_response({"success": True, "membership": membership.to_dict()}, 201)

# 동아리장 승인 API (POST)
@bp.route('/api/approve-membership', methods=['POST'])
def approve_membership():
    data = request.get_json()

    user_id = data.get('user_id')
    club_id = data.get('club_id')

    # 동아리장 이메일 확인
    club = Club.query.get(club_id)
    if not club:
        return json_response({"success": False, "message": "동아리를 찾을 수 없습니다."}, 404)

    # 동아리장만 승인 가능
    if club.leader_email != data.get('leader_email'):
        return json_response({"success": False, "message": "동아리장만 승인할 수 있습니다."}, 403)

    # 해당 회원의 가입 요청 상태가 'pending'인지 확인
    membership = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
    if not membership:
        return json_response({"success": False, "message": "가입 요청을 찾을 수 없습니다."}, 404)

    # 상태 변경: 'approved'로 승인
    membership.status = 'approved'
    db.session.commit()

    return json_response({"success": True, "membership": membership.to_dict()})
