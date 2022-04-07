from core.botcore import BotCore
from requests import post, get
from random import randint
from json.decoder import JSONDecodeError
from sys import platform
from os import getpid
from threading import Thread
from requests.exceptions import ConnectionError

# print("import")
api_url = "https://api.vk.com/method/"  # url для доступа к вк апи
headers = {
    'User-Agent': 'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)'}  # headers для работы методов audio (при использовании нужного ключа)


class Bot(BotCore):
    def __init__(self, name, config):
        # print(f"Инициализация бота {name}")
        super().__init__(name)
        self.default_params = {"v": "5.131",  # Версия апи вк
                               "access_token": config["token"],  # токен группы
                               "disable_mentions": 1,
                               # флаг отключить уведомление об упоминании в сообщении, может принимать значения 1 или 0
                               "dont_parse_links": 1,
                               # флаг отключить регестрирование ссылок об упоминании в сообщении, может принимать значения 1 или 0
                               }
        if config["proxy"]:
            self.proxy = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
        else:
            self.proxy = None
        self.tokens = config["tokens"]
        self.group_id = self.groups.getById()["response"][0]["id"]
        self.names = []  # набор имен, на которые бот будет отзываться (при пустом массиве будет отзываться на все команды)
        for name in config["names"]:
            self.names.append(name.lower())
        self.log_chat = config["log_chat"]  # peer_id для сообщений с информацией
        self.error_chat = config["error_chat"]  # peer_id для сообщений с ошибками
        self.key = None  # секретный ключ сессии
        self.server = None  # адрес сервера
        self.ts = None  # номер последнего события, начиная с которого нужно получать данные
        self.wait = config[
            "vk_wait"]  # время ожидания (так как некоторые прокси-серверы обрывают соединение после 30 секунд, мы рекомендуем указывать wait=25). Максимальное значение — 90.
        # print(f"Инициализация бота {name} закончена")

    def __getattr__(self, method_name):
        return VkAPI(method_name=method_name, default_params=self.default_params, proxy=self.proxy)

    def method(self, method, **params):  # поддержка старых версий ядер
        return VkAPI(method, self.default_params, self.proxy).method(**params)

    def post(self, url, **args):
        return post(url, proxies=self.proxy, **args).json()

    def get(self, url, **args):
        return get(url, proxies=self.proxy, **args).json()

    def send(self, text, **params):
        if "random_id" not in params:
            params["random_id"] = randint(-2147483648, 2147483647)
        send_to_types = ["user_id", "peer_id", "peer_ids", "domain", "chat_id",
                         "reply_to"]  # аргументы используемые для отпарви сообщения
        if not any(x in send_to_types for x in params):  # Если в send не нужен другой получатель (основная функция)
            if self.peed_id:
                return self.messages.send(message=text, peer_id=self.peer_id, **params)
            return
        return self.messages.send(message=text, **params)

    def getLongPollServer(self):
        data = self.groups.getLongPollServer(group_id=self.group_id)["response"]
        self.server = data['server']
        self.ts = data['ts']
        self.key = data['key']

    def start(self):
        th = Thread(target=self.run, daemon=False, name=self._name)
        th.start()

    def __bot_started(self):
        if platform == 'linux':
            print(
                f"Бот \"{self._name}\" запущен. Его pid = {getpid()}\nДля отключения OOM Killer напишите: sudo echo -17 > /proc/{getpid()}/oom_adj")
        else:
            print(f"Бот \"{self._name}\" успешно запущен!")

    def __failed_response(self, response):
        fail = response["failed"]
        if fail == 1:
            print(f"[{self._name}] история событий устарела. Обновление ts")
            self.ts = response['ts']
        elif fail == 2:
            print(f"[{self._name}] истекло время действия ключа. Обновление LP")
            self.getLongPollServer()
        elif fail == 3:
            print(f"[{self._name}] информация устарела. Обновление LP")
            self.getLongPollServer()
        else:
            fail = -1
            print(f"[{self._name}] неизвестная ошибка LP. Обновление LP")
            self.getLongPollServer()

    def __get_response(self):
        fail = 0
        url = f'{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait={self.wait}'
        response = None
        try:
            response = get(url, proxies=self.proxy).json()
            if "failed" in response:
                self.__failed_response(response)
            else:
                self.ts = response['ts']
        except JSONDecodeError:
            fail = -1
            print(f"[{self._name}] Vk LP response was not received in JSON format")
            self.getLongPollServer()
        except ConnectionError as e:
            print(f"[{self._name}] {e}")
        return fail, response

    # TODO сделать для пользователя https://vk.com/dev/using_longpoll
    def run(self):
        self.getLongPollServer()  # получаем сервер LP и данные к нему
        try:
            url = f'{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait={self.wait}'
            response = get(url, proxies=self.proxy).json()
        except JSONDecodeError:
            raise ValueError(f"[{self._name}] Vk LP response was not received in JSON format")
        self.__bot_started()
        while True:
            fail, response = self.__get_response()
            if fail == 0:  # если нет ошибок
                updates = response['updates']  # получение всех обновлений
                for update in updates:  # получение каждого обновления за данный периуд
                    th_update = Thread(target=self.__run_update(update), daemon=False,
                                       name=f"{self._name}_{self.ts}")  # требуется проверить на больших нагрузках
                    th_update.start()
                    # self.__run_update(update)

    def send_error(self, error, from_error):
        msg = f"ошибка при выполнении {from_error}: {error}"
        if self.error_chat:
            self.send(f"[{self._name}]: {msg}", peer_id=self.error_chat)
        print(f"[ERROR] [{self._name}]: {msg}: {error}")

    def __run_event(self):
        if self.event in self.events:
            try:
                self.events[self.event](self)  # вызов эвента
            except Exception as error:
                self.send_error(error, f"эвента {self.event}")

    def __set_cmd_arg_text(self):
        self.cmd = None
        if self.args[0] in self.names:
            if len(self.args) > 1 and self.args[1] in self.cmds:
                self.cmd = self.args[1]  # строка с командой
                self.args = self.args[2:]  # набор аргументов
                self.text = " ".join(
                    self.obj["message"]["text"].split()[2:])  # текст соообщения без обращения и команды
            else:
                self.args = self.args[1:]  # набор аргументов
                self.text = " ".join(
                    self.obj["message"]["text"].split()[1:])  # текст соообщения без обращения и команды
        elif "" in self.names or not self.names:
            if self.args[0] in self.cmds:
                self.cmd = self.args[0]  # строка с командой
                self.args = self.args[1:]  # набор аргументов
                self.text = " ".join(
                    self.obj["message"]["text"].split()[1:])  # текст соообщения без обращения и команды
            else:
                self.text = self.obj["message"]["text"]  # текст соообщения без команды и обращения

    def __set_params(self, conversationMessage: dict):
        self.default_params = self.default_params
        self.from_id = self.obj["message"]["from_id"]
        self.id = conversationMessage["response"]["items"][0]["id"]
        self.fwd = self.obj["message"]["reply_message"] if "reply_message" in self.obj["message"] else \
            self.obj["message"]["fwd_messages"]
        self.attachments = self.obj["message"]["attachments"]
        self.photo = conversationMessage["response"]["profiles"][0]["photo_100"] if "profiles" in conversationMessage[
            "response"] else conversationMessage["response"]["groups"][0]["photo_100"]
        self.name = f'{conversationMessage["response"]["profiles"][0]["first_name"]} {conversationMessage["response"]["profiles"][0]["last_name"]}' if "profiles" in \
                                                                                                                                                       conversationMessage[
                                                                                                                                                           "response"] else \
        conversationMessage["response"]["groups"][0]["name"]

    def __send_log(self, args):
        if (args and args[0] in self.names) or self.peer_id < 2000000000 or self.cmd:
            msg = f"[{self._name}]: сообщение от [id{self.from_id}|{self.name}]({self.peer_id}): {self.obj['message']['text']}"
            print(msg)
            if self.log_chat:
                self.send(msg, peer_id=self.log_chat)

    def __run_cmd(self):
        try:
            self.cmds[self.cmd](self)  # вызов команды
        except Exception as error:
            self.send_error(error, f"команды {self.cmd}")
            self.send(f"Ошибка при выполнение команды, в случае повторных ошибок свяжитесь с администратором")

    def __run_cmd_not_found(self):
        try:
            self.cmd_not_found()  # вызов функции
        except Exception as error:
            self.send_error(error, f"cmd_not_found")
            self.send(f"Ошибка при попытке ответа, в случае повторных ошибок свяжитесь с администратором")

    def __event_cmd(self, conversationMessage):
        self.__set_params(conversationMessage)
        args = self.obj["message"]["text"].lower().split()
        self.__send_log(args)
        if self.cmd:
            self.__run_cmd()
        elif (args[0] in self.names) or (
                self.peer_id == self.from_id):  # если это не команда и обращались к боту, то вызвать cmd_not_found
            self.__run_cmd_not_found()
        else:
            pass  # Если это просто сообщение

    def __new_message(self):
        if self.event == "message_new" and self.obj["message"]["out"] == 0 and self.obj["message"]["from_id"] > 0 and \
                self.obj["message"]["text"]:  # Новое сообщение и оно входящее и от человека
            self.args = self.obj["message"]["text"].lower().split()  # массив аргументов, приведенных в lower
            self.__set_cmd_arg_text()
            conversationMessage = self.messages.getByConversationMessageId(peer_id=self.obj["message"]["peer_id"],
                                                                           conversation_message_ids=self.obj["message"][
                                                                               "conversation_message_id"],
                                                                           extended=1)  # Получаем всю инфу по сообщению
            if conversationMessage["response"]["count"] != 0:
                self.__event_cmd(conversationMessage)

    def __set_pervious_attr(self, update):
        self.obj = update["object"]
        self.event = update["type"]
        self.peer_id = self.obj["message"]["peer_id"] if (("message" in self.obj) and (
                    "peer_id" in self.obj["message"])) else self.log_chat if self.log_chat else None

    def __run_update(self, update):
        self.__set_pervious_attr(update)
        self.__run_event()
        self.__new_message()

    def cmd_not_found(self):
        self.send("Команда не найдена")


class VkAPI:
    def __init__(self, method_name, default_params, proxy=None):
        self.method_name = method_name
        self.default_params = default_params
        self.proxy = proxy

    def __getattr__(self, method_name):
        return VkAPI(f"{self.method_name}.{method_name}", self.default_params, self.proxy)

    def __call__(self, **params):
        return self.method(**params)

    def method(self, **params):
        if self.method_name.lower() == "auth.refresh":
            raise NameError(f"{self.method_name} заблокирован в целях безопастности")
        updated_params = self.default_params.copy()
        updated_params |= params  # python 3.9 (old is "updated_params.update(params)")
        result = post(api_url + self.method_name, data=updated_params, proxies=self.proxy, headers=headers)
        try:
            result = result.json()
        except JSONDecodeError:
            raise ValueError("Vk method response was not received in JSON format")
        if "response" in result:
            return result
        elif "error" in result:
            print(result)
            raise ValueError(result["error"]["error_msg"])

# Вынесено сюда как дополнительная помента о всех эвентах, которые на время написания данного ядра бота Vk
# + добавть эвент no_cmd
# events_types = {
#     "message_new": "входящее сообщение",
#     "message_reply": "новое исходящее сообщение",
#     "message_edit": "редактирование сообщения",
#     "message_allow": "подписка на сообщения от сообщества",
#     "message_deny": "новый запрет сообщений от сообщества",
#     "message_typing_state": "статус набора текста",
#     "message_event": "действие с сообщением. Используется для работы с Callback-кнопками",
#     "photo_new": "добавление фотографии",
#     "photo_comment_new": "добавление комментария к фотографии",
#     "photo_comment_edit": "редактирование комментария к фотографии",
#     "photo_comment_restore": "восстановление комментария к фотографии",
#     "photo_comment_delete": "удаление комментария к фотографии",
#     "audio_new": "добавление аудио",
#     "video_new": "добавление видео",
#     "video_comment_new": "комментарий к видео",
#     "video_comment_edit": "редактирование комментария к видео",
#     "video_comment_restore": "восстановление комментария к видео",
#     "video_comment_delete": "удаление комментария к видео",
#     "wall_post_new": "запись на стене",
#     "wall_repost": "репост записи из сообщества",
#     "wall_reply_new": "добавление комментария на стене",
#     "wall_reply_edit": "редактирование комментария на стене",
#     "wall_reply_restore": "восстановление комментария на стене",
#     "wall_reply_delete": "удаление комментария на стене",
#     "like_add": "Событие о новой отметке \"Мне нравится\"",
#     "like_remove": "Событие о снятии отметки \"Мне нравится\"",
#     "board_post_new": "создание комментария в обсуждении",
#     "board_post_edit": "редактирование комментария",
#     "board_post_restore": "восстановление комментария",
#     "board_post_delete": "удаление комментария в обсуждении",
#     "market_comment_new": "новый комментарий к товару",
#     "market_comment_edit": "редактирование комментария к товару",
#     "market_comment_restore": "восстановление комментария к товару",
#     "market_comment_delete": "удаление комментария к товару",
#     "market_order_new": "новый заказ",
#     "market_order_edit": "редактирование заказа",
#     "group_leave": "удаление участника из сообщества",
#     "group_join": "добавление участника или заявки на вступление в сообщество",
#     "user_block": "добавление пользователя в чёрный список",
#     "user_unblock": "удаление пользователя из чёрного списка",
#     "poll_vote_new": "добавление голоса в публичном опросе",
#     "group_officers_edit": "редактирование списка руководителей",
#     "group_change_settings": "изменение настроек сообщества",
#     "group_change_photo": "изменение главного фото",
#     "vkpay_transaction": "платёж через VK Pay",
#     "app_payload": "Событие в VK Mini Apps",
#     "donut_subscription_create": "создание подписки",
#     "donut_subscription_prolonged": "продление подписки",
#     "donut_subscription_expired": "подписка истекла",
#     "donut_subscription_cancelled": "отмена подписки",
#     "donut_subscription_price_changed": "изменение стоимости подписки",
#     "donut_money_withdraw": "вывод денег",
#     "donut_money_withdraw_error": "ошибка вывода денег"
# }
