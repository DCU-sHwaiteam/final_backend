# app/routes/club.py

from flask import Blueprint, make_response, request, jsonify
from app.models.club import Club
from app.models.user import User
from app.models.clubmembership import ClubMembership
from sqlalchemy import func
import json
from app import db

bp = Blueprint('club', __name__)

# 한글 응답용 JSON 함수
def json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, status

@bp.route('/api/create-club', methods=['POST'])
def create_club():
    data = request.get_json()

    required_fields = ['name', 'leaderEmail', 'advisor', 'maxMembers']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "message": f"{field} 값이 누락되었습니다."}), 400

    # leader_email 유효성 확인
    leader_email = data.get('leaderEmail')
    print("leader_email from frontend:", leader_email)

    user = User.query.filter(func.lower(User.email) == leader_email.lower()).first()

    if not user:
        return jsonify({"success": False, "message": "유효하지 않은 동아리장 이메일입니다."}), 400


    # 중복 동아리명 방지
    if Club.query.filter_by(name=data.get('name')).first():
        return jsonify({"success": False, "message": "이미 존재하는 동아리 이름입니다."}), 409

    # 현재 인원 > 최대 인원 방지
    if int(data.get('currentMembers', 0)) > int(data.get('maxMembers', 0)):
        return jsonify({"success": False, "message": "현재 인원이 최대 인원을 초과할 수 없습니다."}), 400

    new_club = Club(
        name=data['name'],
        leader_email=leader_email,
        leader_name=user.name,
        advisor=data['advisor'],
        max_members=data['maxMembers'],
        current_members=data.get('currentMembers', 0),
        activity_schedule=data.get('activitySchedule'),
        tags=data.get('tags'),
        description=data.get('description')
    )

    db.session.add(new_club)
    db.session.commit()

  # 동아리장도 ClubMembership에 status='approved'로 추가!
    club_leader_membership = ClubMembership(
        user_id=user.id,
        club_id=new_club.id,
        status='approved'
    )
    db.session.add(club_leader_membership)
    db.session.commit()
    
    return jsonify({"success": True, "club": new_club.to_dict()}), 201
    

@bp.route('/api/clubs', methods=['GET'])
def get_clubs():
    from flask import request

    keyword = request.args.get('search', '').strip()

    if keyword:
        clubs = Club.query.filter(Club.name.like(f"%{keyword}%")).all()
    else:
        clubs = Club.query.all()

    return jsonify([club.to_dict() for club in clubs]), 200   
