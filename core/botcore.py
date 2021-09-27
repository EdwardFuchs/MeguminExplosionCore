import sys
from typing import List, Any

class Bot:
    def __init__(self, name):
        self._name = name
        self.cmds = {}  # список команд с привязкой
        self.events = {}  # список эвенов с привязкой
        self.imported = {}  # список всех заимпортированных файлов и храняшихся в нем эвентов и комманд

    def _add_plugin(self, path):
        path_to_import = self.__reformat_path(path)
        try:
            if path_to_import not in sys.modules:
                import_cmd = __import__(path_to_import, fromlist=["cmd", "event"])
            else:
                # import_cmd = importlib.reload(path_to_import)
                sys.modules.pop(path_to_import)
                import_cmd = __import__(path_to_import, fromlist=["cmd", "event"])
            # print(dir(import_cmd))
            cmd = None
            event = None
            if "cmd" in dir(import_cmd):
                cmd = import_cmd.cmd
            if "event" in dir(import_cmd):
                event = import_cmd.event
            if path_to_import not in self.imported:
                self.imported[path_to_import] = {"cmds": [], "events": []}
            return self.__reload_plugins(path_to_import=path_to_import, cmd=cmd, event=event)
        except Exception as e:  # TODO чат с ошибками
            msg = f"Exception: Не получилось импортиовать файл {path} с ошибкой {e}"
            print(msg)
        return None, None, None, None, None, None

    def _del_plugin(self, path):  # Для использования в плагинах опытными пользователями
        path_to_import = self.__reformat_path(path)
        if path_to_import in sys.modules:
            sys.modules.pop(path_to_import)
            msg = f"Модуль {path} удален"
            return msg
        else:
            msg = f"Модуль {path} не найден"
            return msg

    @staticmethod
    def __reformat_path(path):
        return path.replace("/", ".").replace("\\", ".").replace(".py", "")

    @staticmethod
    def __to_good_format(d: dict):
        """Приводит словари команд и эвентов к общему виду"""
        for key in d.keys():
            if not isinstance(d[key], list):
                d[key] = [d[key]]
        return d

    def __is_func_used(self, func):  # используется ли функция в командах или эвентах
        for key in self.cmds.keys():
            if func == self.cmds[key]:
                return True
        for key in self.events.keys():
            if func == self.events[key]:
                return True
        return False

    def __reload_cmd(self, path_to_import, cmd):
        add_cmd = []
        update_cmd = []
        deleted_cmd = []
        if cmd:
            cmd = self.__to_good_format(cmd)
            for func in cmd.keys():
                for com in cmd[func]:
                    com = com.lower()
                    if com not in self.cmds:
                        add_cmd.append(com)
                        self.imported[path_to_import]["cmds"].append(com)
                    else:
                        update_cmd.append(com)
                    self.cmds[com] = func
            deleted_cmd = [item for item in self.imported[path_to_import]["cmds"] if item not in (add_cmd + update_cmd)]
            for com in deleted_cmd:
                self.imported[path_to_import]["cmds"].remove(com)
                func = self.cmds.pop(com)  # возвращает функцию
                if not self.__is_func_used(func):  # если функция нигде не используется то удалить ее
                    del func
        return add_cmd, update_cmd, deleted_cmd

    def __reload_event(self, path_to_import, event):
        add_event = []
        update_event = []
        deleted_event = []
        if event:
            event = self.__to_good_format(event)
            for func in event.keys():
                for ev in event[func]:
                    ev = ev.lower()
                    if ev not in self.events:
                        add_event.append(ev)
                        self.imported[path_to_import]["events"].append(ev.lower())
                    else:
                        update_event.append(ev)
                    self.events[ev] = func
            deleted_event = [item for item in self.imported[path_to_import]["events"] if
                             item not in (add_event + update_event)]
            for ev in deleted_event:
                self.imported[path_to_import]["events"].remove(ev)
                func = self.events.pop(ev)  # возвращает функцию
                if not self.__is_func_used(func):  # если функция нигде не используется то удалить ее
                    del func
        return add_event, update_event, deleted_event

    def __reload_plugins(self, path_to_import: str, cmd: dict = None, event: dict = None):  # TODO удалить если пустой cmd или event (если до этого был не пустым)
        return self.__reload_cmd(path_to_import, cmd) + self.__reload_event(path_to_import, event)
        # raise ValueError("cmd или event должны быть заданы")

    @staticmethod
    def run():
        print("Оболочка не инициализирована")
