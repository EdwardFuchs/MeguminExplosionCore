from re import fullmatch

from sqlalchemy.orm import Query

from core.models.models import PrivilegesGroups


def privileges(bot):
    # bot.user.group = "Admin"
    # bot.db.commit()
    # bot.send(bot.user.group)
    priveleges_group: Query = bot.db.query(PrivilegesGroups).filter_by(group=bot.user.group) # .filter(PrivilegesGroups.allow.like(bot.text)).all()
    bad = priveleges_group.filter(PrivilegesGroups.allow.like('-%')).all()
    bad = [x.allow for x in bad]
    f, s = bot.text.split(".")
    pattern = r"-?(:?\*|" + f + r")\.(:?\*|" + s + r")"
    if next(filter(lambda x: fullmatch(pattern, x), bad), None):
        bot.send("Can't use")
        return
    good = priveleges_group.filter(PrivilegesGroups.allow.not_in(bad)).all()
    good = [x.allow for x in good]
    if next(filter(lambda x: fullmatch(pattern, x), good), None):
        bot.send('Can use')

    # # bad = map(lambda x: x.allow, bad)
    # bad = [x.allow for x in bad]
    # print(type(bad))
    # good = priveleges_group.filter(PrivilegesGroups.allow.not_in(bad)).all()
    # good = [x.allow for x in good]
    # # good = map(lambda x: x.allow, good)
    # bot.send(str(list(bad)))
    # bot.send(str(list(good)))
    # if bot.text in bad or bot.text not in good:
    #     bot.send("No Priliv")
    # first, second = bot.text.split('.')
    # # bad_list = [x.split('.') for x in bad]
    # # good_list = [x.split('.') for x in good]
    # bad = [x[1:] for x in bad]
    # f, s = bot.text.split(".")
    # pattern = r"(:?\*|"+f+r")\.(:?\*|"+s+r")"
    # test_bad = filter(lambda x: fullmatch(pattern, x), bad)
    # test_good = filter(lambda x: fullmatch(pattern, x), good)
    # bot.send(f"{[*test_good]=}")
    # bot.send(f"{[*test_bad]=}")
    # # TODO *.text, text.*, *.*
    # # bot.db


cmd = {
    privileges: ["t"],
}
