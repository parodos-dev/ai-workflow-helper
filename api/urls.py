from api.chat import list_chats, create_new_chat


urls = [
    ("/chat", list_chats, ['GET']),
    ("/chat", create_new_chat, ['POST'])
]
