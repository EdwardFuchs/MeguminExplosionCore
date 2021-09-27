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
            self.file_updater[event.src_path] = int(time.time())

    def on_created(self, event):
        if not event.is_directory:
            self.file_updater[event.src_path] = int(time.time())

    def on_deleted(self, event):  # TODO удаление плагина и всего его содержимого
        if not event.is_directory:
            self.file_updater[event.src_path] = int(time.time())

    def __updater(self, time_to_check_update):
        while True:
            for src in list(self.file_updater):
                if src[-1:] != "~" and self.file_updater[src] + time_to_check_update < int(
                        time.time()):  # Странно почему начало добавляеть ~
                    del self.file_updater[src]
                    print(f"[{self.bot._name}]: информация о импорте:\n{self.__gen_text(*self.bot._add_plugin(src))}")
                    print(f'[{self.bot._name}]: изменен файл "{src}"')
            time.sleep(time_to_check_update / 4)

    @staticmethod
    def __gen_text(add_cmd, update_cmd, deleted_cmd, add_event, update_event, deleted_event):
        res = []
        add_cmd_text = "команда" if len(add_cmd) > 1 else "команды"
        update_cmd_text = "команда" if len(update_cmd) > 1 else "команды"
        deleted_cmd_text = "команда" if len(deleted_cmd) > 1 else "команды"
        add_event_text = "эвент" if len(add_event) > 1 else "эвенты"
        update_event_text = "эвент" if len(update_event) > 1 else "эвенты"
        deleted_event_text = "эвент" if len(deleted_event) > 1 else "эвенты"
        if add_cmd:
            add_cmd = ", ".join(add_cmd)
            res.append(f"Добавлены {add_cmd_text}: {add_cmd}")
        if update_cmd:
            update_cmd = ", ".join(update_cmd)
            res.append(f"Добавлены {update_cmd_text}: {update_cmd}")
        if deleted_cmd:
            deleted_cmd = ", ".join(deleted_cmd)
            res.append(f"Добавлены {deleted_cmd_text}: {deleted_cmd}")
        if add_event:
            add_event = ", ".join(add_event)
            res.append(f"Добавлены {add_event_text}: {add_event}")
        if update_event:
            update_event = ", ".join(update_event)
            res.append(f"Добавлены {update_event_text}: {update_event}")
        if deleted_event:
            deleted_event = ", ".join(deleted_event)
            res.append(f"Добавлены {deleted_event_text}: {deleted_event}")
        return "\n".join(res)
