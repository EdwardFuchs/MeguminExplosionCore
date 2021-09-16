import sys


class Bot:
    def __init__(self, name, config=None):
        self.cmds = {}
        self.config = config

    def _add_cmd(self, path):
        path_to_import = self.__reformat_path(path)
        try:
            if path_to_import not in sys.modules:
                import_cmd = __import__(path_to_import, fromlist=["cmd"])
            else:
                # import_cmd = importlib.reload(path_to_import)
                sys.modules.pop(path_to_import)
                import_cmd = __import__(path_to_import, fromlist=["cmd"])
            cmd = import_cmd.cmd
            msg = self.__reload_cmds(cmd)
            return msg
        except Exception as e:
            msg = f"Не получилось импортиовать файл {path} с ошибкой {e}"
            return msg

    def _del_cmd(self, path):
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

    def __reload_cmds(self, cmd):
        res = "Добавлены команда(ы): {add_cmd}\n" \
              "Обновлены команда(ы): {update_cmd}\n" \
              "Удалены команда(ы): {deleted_cmd}"
        add_cmd = []
        update_cmd = []
        deleted_cmd = []
        for com in list(cmd):
            if com not in self.cmds:
                add_cmd.append(com)
            else:
                update_cmd.append(com)
            self.cmds[com] = cmd[com]
        res = res.format(add_cmd=', '.join(add_cmd), update_cmd=', '.join(update_cmd),
                         deleted_cmd=', '.join(deleted_cmd))
        return res

    @staticmethod
    def run():
        print("Оболочка не инициализирована")
