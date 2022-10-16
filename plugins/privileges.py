from re import fullmatch

from sqlalchemy.orm import Query

from core.models.models import PrivilegesGroups


def privileges_func(bot):
    bot.send('t command')


cmd = {
    privileges_func: ["t"],
}
