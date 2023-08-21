class Utils:
    mumbleManager = None

    @staticmethod
    def close():
        print("Stopping...")
        if Utils.mumbleManager is not None:
            Utils.mumbleManager.close()
        else:
            print("No ICE connection to delete. (not an error)")
        exit()

    @staticmethod
    def get_user(server, userid):
        try:
            return [u for u in list(server.getUsers().values()) if int(u.userid) == int(userid)][0]
        except (ValueError, IndexError):
            return None
