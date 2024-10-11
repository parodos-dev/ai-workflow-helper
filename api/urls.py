from api.chat import list_chats, create_new_chat, get_chat, push_new_message
from api.chat import get_workflow, get_all_workflow
from api.static import index_page

urls = [
    ("/chat", list_chats, ['GET']),
    ("/chat", create_new_chat, ['POST']),
    ("/chat/<session_id>", get_chat, ['GET']),
    ("/chat/<session_id>/workflow", get_workflow, ['GET']),
    ("/chat/<session_id>/workflows", get_all_workflow, ['GET']),
    ("/chat/<session_id>", push_new_message, ['POST']),
    ("/", index_page, ['GET']),
]
