from api.chat import list_chats, create_new_chat, get_chat


urls = [
    ("/chat", list_chats, ['GET']),
    ("/chat", create_new_chat, ['POST']),
    ("/chat/<session_id>", get_chat, ['GET']),
]
