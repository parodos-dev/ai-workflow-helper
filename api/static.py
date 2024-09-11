from flask import send_from_directory


def index_page():
    return send_from_directory('static', 'index.html')
