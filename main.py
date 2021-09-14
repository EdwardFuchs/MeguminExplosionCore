from os import listdir
from json import loads
from threading import Thread

from core.cores import *
from core.updater import UpdaterHandler
from watchdog.observers import Observer


def get_bots():
    bots = []
    for bot in listdir("bots"):
        bot_name = ".".join(bot.split(".")[:-1])
        with open(f"./bots/{bot}") as file:
            bot = loads(file.read())
        if not bot["enable"]:
            continue
        mybot = {}
        try:
            exec(fr"mybot = {bot['bot_lib']}('{bot_name}', {bot[bot['bot_lib']]})", globals(),
                 mybot)  # Возможно есть более лучший способ
            bots.append(Thread(target=mybot["mybot"].run, daemon=False, name=bot_name))
        except Exception as e:
            print(f"ERROR [{bot_name}]: {e}")
    return bots


def run_bots(bots):
    for bot in bots:
        updater = UpdaterHandler(bot, time_to_check_update=0.5)
        observer = Observer()
        observer.schedule(updater, path='plugins', recursive=False)
        observer.start()
        bot.start()


def main():
    print("Инициализация ботов")
    bots = get_bots()
    print("Инициализация ботов закончена")
    print()
    print(f"Запуск ботов: {', '.join([x.name for x in bots])}")
    run_bots(bots)


if __name__ == "__main__":
    main()
