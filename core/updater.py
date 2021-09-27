from watchdog.events import FileSystemEventHandler
from threading import Thread
import time
from os import listdir
from os.path import isfile, join


class UpdaterHandler(FileSystemEventHandler):

    def __init__(self, bot, plugins_path="plugins", time_to_check_update=1):
        self.bot = bot
        self.file_updater = {}
        res = [[], [], [], [], [], []]
        files = [f for f in listdir(plugins_path) if isfile(join(plugins_path, f))]
        for file in files:
            added = self.bot._add_plugin(join(plugins_path, file))
            for i, add in enumerate(added):
                if add:
                    res[i] += add
        print(f"[{self.bot._name}] информация о импорте:\n{self.__gen_text(*res)}")
        updater = Thread(target=self.__updater, args=[time_to_check_update])
        updater.start()

    def on_modified(self, event):
        if not event.is_directory:
            self.file_updater[event.src_path] = {}
            self.file_updater[event.src_path]["time"] = int(time.time())
            self.file_updater[event.src_path]["type"] = "modified"

    def on_created(self, event):
        self.on_modified(event)

    def on_deleted(self, event):
        if not event.is_directory:
            self.file_updater[event.src_path] = {}
            self.file_updater[event.src_path]["time"] = int(time.time())
            self.file_updater[event.src_path]["type"] = "deleted"

    def __updater(self, time_to_check_update):
        while True:
            for src in list(self.file_updater):
                if src[-1:] != "~" and self.file_updater[src]["time"] + time_to_check_update < int(time.time()):  # Странно почему начало добавляеть ~
                    if self.file_updater[src]["type"] == "modified":
                        add = self.__gen_text(*self.bot._add_plugin(src))
                    else:
                        add = self.__gen_text(*self.bot._del_plugin(src))
                    del self.file_updater[src]
                    print(f"[{self.bot._name}]: информация о импорте:\n{add}")
                    print(f'[{self.bot._name}]: изменен файл "{src}"')
            time.sleep(time_to_check_update / 4)

    @staticmethod
    def __gen_text_cmd(*args):
        res = []
        updates = {
            "0": ["Добавлена", "Обновлена", "Удалена", "команда"],
            "1": ["Добавлены", "Обновлены", "Удалены", "команды"]
        }
        for i, arg in enumerate(args):
            if arg:
                multi = "1" if len(arg) > 1 else "0"
                res.append(f"{updates[multi][i]} {updates[multi][-1]}: {', '.join(arg)}")
        return res

    @staticmethod
    def __gen_text_event(*args):
        res = []
        updates = {
            "0": ["Добавлен", "Обновлен", "Удален", "эвент"],
            "1": ["Добавлены", "Обновлены", "Удалены", "эвент"]
        }
        for i, arg in enumerate(args):
            if arg:
                multi = "1" if len(arg) > 1 else "0"
                res.append(f"{updates[multi][i]} {updates[multi][-1]}: {', '.join(arg)}")
        return res

    def __gen_text(self, *args):
        res = []
        res += self.__gen_text_cmd(*args[:3])
        res += self.__gen_text_event(*args[3:])
        return "\n".join(res)
