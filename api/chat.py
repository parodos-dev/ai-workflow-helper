import uuid
import logging

from flask import jsonify, g, Response, request
from services.chats import get_response_for_session, get_history, get_all_workflow_for_session, get_workflow_for_session

def list_chats():
    sessions = g.ctx.history_repo.get_all_sessions()
    return jsonify(sessions)


def create_new_chat():
    session_id = uuid.uuid4()
    user_input = request.json.get("input", "")
    if len(user_input) == 0:
        return Response("Invalid user input", status=400)
    content = get_response_for_session(g.ctx, session_id, user_input)
    response = Response(content, mimetype='text/html')
    response.headers["session_id"] = session_id
    return response


def get_chat(session_id):
    messages = [x.dict() for x in get_history(g.ctx, session_id)]
    return jsonify(messages)


def get_workflow(session_id):
    content = get_workflow_for_session(g.ctx, session_id)
    return content

def get_all_workflow(session_id):
    content = get_all_workflow_for_session(g.ctx, session_id)
    return content


def push_new_message(session_id):
    logging.debug("push_new_message start")
    user_input = request.json.get("input", "")
    if len(user_input) == 0:
        return Response("Invalid user input", status=400)
    content = get_response_for_session(g.ctx, session_id, user_input)
    return Response(content, mimetype='text/html')
