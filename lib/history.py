from langchain_community.chat_message_histories import SQLChatMessageHistory


class HistoryRepository(SQLChatMessageHistory):
    def get_all_sessions(self):
        sessions = []
        with self._make_sync_session() as session:
            result = (
                session.query(
                    getattr(self.sql_model_class, self.session_id_field_name))
                .distinct()
                .order_by(self.sql_model_class.id.asc())
            )
            for x in result:
                sessions.append(x[0])
        return sessions
