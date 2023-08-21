class Utils:
    @staticmethod
    def get_user(server, userid):
        try:
            return [
                u for u in list(
                    server.getUsers().values()) if int(
                    u.userid) == int(userid)][0]
        except (ValueError, IndexError):
            return None
