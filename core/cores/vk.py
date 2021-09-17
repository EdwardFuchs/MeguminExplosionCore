from core.botcore import Bot
from requests import post, get
from random import randint
from json.decoder import JSONDecodeError
from sys import platform
from os import getpid
from threading import Thread

# print("import")
api_url = "https://api.vk.com/method/"  # url для доступа к вк апи


class Vk(Bot):
    def __init__(self, name, config):
        # print(f"Инициализация бота {name}")
        super().__init__()
        self.name = name
        self.default_params = {"v": "5.131",  # Версия апи вк
                               "access_token": config["token"],  # токен группы
                               "disable_mentions": 1,  # флаг отключить уведомление об упоминании в сообщении, может принимать значения 1 или 0
                               "dont_parse_links": 1,  # флаг отключить регестрирование ссылок об упоминании в сообщении, может принимать значения 1 или 0
                               }
        if config["proxy"]:
            self.proxy = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
        else:
            self.proxy = None
        self.group_id = self.groups.getById()["response"][0]["id"]

        # self.disable_mentions = 1  # флаг: отключить уведомление об упоминании в сообщении, может принимать значения 1 или 0
        # self.dont_parse_links = 1  # флаг: не создавать сниппет ссылки из сообщения, может принимать значения 1 или 0
        self.key = None  # секретный ключ сессии
        self.server = None  # адрес сервера
        self.ts = None  # номер последнего события, начиная с которого нужно получать данные
        self.wait = config["vk_wait"]  # время ожидания (так как некоторые прокси-серверы обрывают соединение после 30 секунд, мы рекомендуем указывать wait=25). Максимальное значение — 90.
        # print(f"Инициализация бота {name} закончена")

    def __getattr__(self, method_name):
        return VkAPI(method_name=method_name, default_params=self.default_params, proxy=self.proxy)

    def method(self, method, **params):  # поддержка старых версий ядер
        # TODO сделать через класс VkAPI
        pass
        # updated_params = self.default_params.copy()  # копирлвание стандартных параметров
        # updated_params |= params  # python 3.9 (old is "updated_params.update(params)")
        # request_url = f"{api_url}/{method}"
        # # if "type" in params and params["type"] == "get":
        # #     result = get(request_url, params=params, proxies=self.proxy, timeout=30)
        # # else:
        # result = post(request_url, data=params, proxies=self.proxy, timeout=30)
        # try:
        #     result = result.json()
        # except JSONDecodeError:
        #     # TODO сделать отправку в ошибочный чат
        #     pass
        # if "error" in result:
        #     # TODO на рассмотрении
        #     pass
        # return result

    def send(self, text, **params):
        print(self.peer_id)
        if "random_id" not in params:
            params["random_id"] = randint(-2147483648, 2147483647)
        send_to_types = ["user_id", "peer_id", "peer_ids", "domain", "chat_id", "reply_to"]  # аргументы используемые для отпарви сообщения
        if not any(x in send_to_types for x in params):  # Если в send не нужен другой получатель (основная функция)
            return self.messages.send(message=text, peer_id=self.peer_id, **params)
        return self.messages.send(**params)

    def getLongPollServer(self):
        data = self.groups.getLongPollServer(group_id=self.group_id)["response"]
        self.server = data['server']
        self.ts = data['ts']
        self.key = data['key']

    def start(self):
        th = Thread(target=self.run, daemon=False, name=self.name)
        th.start()

    # TODO сделать для пользователя https://vk.com/dev/using_longpoll
    def run(self):
        self.getLongPollServer()  # получаем сервер LP и данные к нему
        try:
            url = f'{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait={self.wait}'
            response = get(url, proxies=self.proxy).json()
        except JSONDecodeError:
            raise ValueError(f"[{self.name}] Vk LP response was not received in JSON format")
        if platform == 'linux':
            print(
                f"Бот \"{self.name}\" запущен. Его pid = {getpid()}\nДля отключения OOM Killer напишите: sudo echo -17 > /proc/{getpid()}/oom_adj")
        else:
            print(f"Бот \"{self.name}\" успешно запущен!")
        while True:
            fail = 0
            try:
                url = f'{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait={self.wait}'
                response = get(url, proxies=self.proxy).json()
                if "failed" in response:
                    fail = response["failed"]
                    if fail == 1:
                        print(f"[{self.name}] история событий устарела. Обновление ts")
                        self.ts = response['ts']
                    elif fail == 2:
                        print(f"[{self.name}] истекло время действия ключа. Обновление LP")
                        self.getLongPollServer()
                    elif fail == 3:
                        print(f"[{self.name}] информация устарела. Обновление LP")
                        self.getLongPollServer()
                    else:
                        fail = -1
                        self.getLongPollServer()
                        print(f"[{self.name}] неизвестная ошибка LP. Обновление LP")
                else:
                    self.ts = response['ts']
            except JSONDecodeError:
                fail = -1
                self.getLongPollServer()
                print(f"[{self.name}] Vk LP response was not received in JSON format")
            if fail == 0:  # если нет ошибок
                updates = response['updates']  # получение всех обновлений
                for update in updates:  # получение каждого обновления
                    self.__run_update(update)  # TODO каждое обновление в новый поток

    def __run_update(self, update):
        obj = update["object"]
        # TODO добавить привязку эвентов ДО message_new
        if update["type"] == "message_new" and obj["out"] == 0:
            print(f"новое сообщение от {obj['from_id']} из {obj['peer_id']}: {obj['text']}")
            conversationMessage = self.messages.getByConversationMessageId(peer_id=obj["peer_id"], conversation_message_ids=obj["conversation_message_id"], extended=1)  # Получаем всю инфу по сообщению
            self.peer_id = obj["peer_id"]
            self.default_params = self.default_params
            self.from_id = obj["from_id"]
            self.id = conversationMessage["response"]["items"][0]["id"]
            self.text = obj["text"]
            self.args = obj["text"]  # массив аргументов
            self.cmd = obj["text"]  # строка с командой
            self.fwd_messages = obj["fwd_messages"]
            self.attachments = obj["attachments"]
            self.photo = conversationMessage["response"]["profiles"][0]["photo_100"]
            self.first_name = conversationMessage["response"]["profiles"][0]["first_name"]
            self.last_name = conversationMessage["response"]["profiles"][0]["last_name"]
            self.obj = obj
            # vk.peer_id = 557539687
            self.send(text="qq")
            # print(conversationMessage)
            # print(self.messages.send(
            #     peer_id=obj["peer_id"],
            #     random_id=0,
            #     message="ответочка",
            #     reply_to=conversationMessage["response"]["items"][0]["id"]
            # ))


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
        result = post(api_url + self.method_name, data=updated_params, proxies=self.proxy)
        try:
            result = result.json()
        except JSONDecodeError:
            raise ValueError("Vk method response was not received in JSON format")
        if "response" in result:
            return result
        elif "error" in result:
            raise ValueError(result["error"]["error_msg"])


# event = {
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
