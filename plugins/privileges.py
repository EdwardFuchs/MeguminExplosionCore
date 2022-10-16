from core.models.models import Privileges


def privileges(bot):
    Privileges(user_id=bot.user.id, allow=bot.text)
    # bot.db


cmd = {
    privileges: ["t"],
}
