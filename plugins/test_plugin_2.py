def say(bot):
    bot.send(f'Была вызвана команда "{bot.cmd}"')


def wall_post_new(bot):
    bot.send(f"Вывыан эвент {bot.event}")


def get_chat(bot):
    res = 1/0
    bot.send(f"{bot.peer_id}")


cmd = {say: "cmd", get_chat: "getchat"}


event = {wall_post_new: ["wall_post_new"]}



