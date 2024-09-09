from flask import jsonify
from flask import g


def list_chats():
    sessions = g.ctx.historyRepo.get_all_sessions()
    return jsonify(sessions)
