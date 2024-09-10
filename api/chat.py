import uuid

from flask import jsonify, g, Response, request
from services.chats import get_response_for_session


def list_chats():
    sessions = g.ctx.historyRepo.get_all_sessions()
    return jsonify(sessions)


def create_new_chat():
    session_id = uuid.uuid4()
    user_input = request.json.get("input", "")
    if len(user_input) == 0:
        return Response("Invalid user input", status=400)

    response = get_response_for_session(g.ctx, session_id, user_input)
    return Response(response, mimetype='text/html')
