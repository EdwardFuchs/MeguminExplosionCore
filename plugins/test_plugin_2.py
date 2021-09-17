def say(event):
    print("Была вызвана команда 'cmd'")


def say2(event):
    print("Был вызван эвент 'vk_message_new'")


cmd = {say: "cmd"}


event = {say: ["vk_message_new"]}





