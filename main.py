from os import listdir
from json import loads

# from core.cores import *
from importlib import import_module
from core.updater import UpdaterHandler
from watchdog.observers import Observer
# PIP_TARGET=/path/to/pip/dir - переменная среды


def get_bots():
    bots = {}
    for bot in listdir("bots"):
        bot_name = ".".join(bot.split(".")[:-1])
        with open(f"./bots/{bot}", encoding="utf-8") as file:
            bot = loads(file.read())
        if not bot["enable"]:
            continue
        try:
            mybot = import_module(f"..{bot['bot_lib']}", "core.cores.").Bot(bot_name, bot["cfg"])
            bots[bot_name] = {}
            bots[bot_name]["bot"] = mybot
            bots[bot_name]["plugins_path"] = bot["plugins_path"]
            bots[bot_name]["time_to_check_update"] = bot["time_to_check_update"]
        except Exception as e:
            print(f"ERROR [{bot_name}]: {e}")
    return bots


def run_bots(bots):
    for bot_name in bots:
        bot = bots[bot_name]["bot"]
        plugins_path = bots[bot_name]["plugins_path"]
        time_to_check_update = bots[bot_name]["time_to_check_update"]
        updater = UpdaterHandler(bot, time_to_check_update=time_to_check_update, plugins_path=plugins_path)
        observer = Observer()
        observer.schedule(updater, path=plugins_path, recursive=False)
        observer.start()
        bot.start()


def main():
    print("Инициализация ботов")
    bots = get_bots()
    print("Инициализация ботов закончена")
    print()
    print(f"Запуск ботов: {', '.join([_ for _ in bots.keys()])}")
    run_bots(bots)


if __name__ == "__main__":
    main()
