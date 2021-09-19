import sys
from typing import List, Any


class Bot:
    def __init__(self):
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
            msg = ""
            cmd = None
            event = None
            if "cmd" in dir(import_cmd):
                cmd = import_cmd.cmd
            if "event" in dir(import_cmd):
                event = import_cmd.event
            if path_to_import not in self.imported:
                self.imported[path_to_import] = {"cmds": [], "events": []}
            msg += self.__reload_plugins(path_to_import=path_to_import, cmd=cmd, event=event) + "\n"
            return msg
        except ValueError as e:
            msg = f"Не получилось импортиовать файл {path} с ошибкой {e}"
            return msg

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

    def __reload_plugins(self, path_to_import: str, cmd: dict = None, event: dict = None):
        res = ""
        if cmd:
            cmd = self.__to_good_format(cmd)
            res += "Добавлена(ы) команда(ы): {add_cmd}\n" \
                   "Обновлена(ы) команда(ы): {update_cmd}\n" \
                   "Удалена(ы) команда(ы): {deleted_cmd}\n"
            add_cmd = []
            update_cmd = []
            for func in cmd.keys():
                for com in cmd[func]:
                    if com not in self.cmds:
                        add_cmd.append(com)
                        self.imported[path_to_import]["cmds"].append(com)
                    else:
                        update_cmd.append(com)
                    self.cmds[com] = func
            deleted_cmd = [item for item in self.imported[path_to_import]["cmds"] if item not in (add_cmd+update_cmd)]
            for com in deleted_cmd:
                self.imported[path_to_import]["cmds"].remove(com)
                func = self.cmds.pop(com)  # возвращает функцию
                if not self.__is_func_used(func):  # если функция нигде не используется то удалить ее
                    del func
            res = res.format(add_cmd=', '.join(add_cmd), update_cmd=', '.join(update_cmd), deleted_cmd=', '.join(deleted_cmd))
        if event:
            event = self.__to_good_format(event)
            res += "Добавлен(ы) эвент(ы): {add_event}\n" \
                   "Обновлен(ы) эвент(ы): {update_event}\n" \
                   "Удален(ы) эвент(ы): {deleted_event}\n"
            add_event = []
            update_event = []
            for func in event.keys():
                for ev in event[func]:
                    if ev not in self.events:
                        add_event.append(ev)
                        self.imported[path_to_import]["events"].append(ev)
                    else:
                        update_event.append(ev)
                    self.events[ev] = func
            deleted_event = [item for item in self.imported[path_to_import]["events"] if item not in (add_event + update_event)]
            for ev in deleted_event:
                self.imported[path_to_import]["events"].remove(ev)
                func = self.events.pop(ev)  # возвращает функцию
                if not self.__is_func_used(func):  # если функция нигде не используется то удалить ее
                    del func
            res = res.format(add_event=', '.join(add_event), update_event=', '.join(update_event), deleted_event=', '.join(deleted_event))
        if res:
            return res
        raise ValueError("cmd или event должны быть заданы")

    @staticmethod
    def run():
        print("Оболочка не инициализирована")
