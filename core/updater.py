from watchdog.events import FileSystemEventHandler
from threading import Thread
import time


class UpdaterHandler(FileSystemEventHandler):

    def __init__(self, bot, plugins_path="plugins", time_to_check_update=1):
        self.bot = bot
        self.file_updater = {}
        # TODO первоночальная загрузка эвентов
        updater = Thread(target=self.__updater, args=[time_to_check_update])
        updater.start()

    def on_modified(self, event):
        if not event.is_directory:
            self.file_updater[event.src_path] = int(time.time())

    def on_created(self, event):
        if not event.is_directory:
            self.file_updater[event.src_path] = int(time.time())

    # TODO удаление файлов с плагина
    def on_deleted(self, event):
        if not event.is_directory:
            self.file_updater[event.src_path] = int(time.time())

    def __updater(self, time_to_check_update):
        while True:
            for src in list(self.file_updater):
                if src[-1:] != "~" and self.file_updater[src] + time_to_check_update < int(time.time()):  # Странно почему начало добавляеть ~
                    del self.file_updater[src]
                    print(self.bot._add_plugin(src))
                    print(f"Изменен: {src}")
            time.sleep(time_to_check_update / 4)
