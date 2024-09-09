from api.chat import list_chats


urls = [
    ("/chat", list_chats, ['GET'])
]
