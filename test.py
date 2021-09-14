# class API(object):
#     def __init__(self, session, timeout=10, **method_default_args):
#         self._session = session
#         self._timeout = timeout
#         self._method_default_args = method_default_args
#
#     def __getattr__(self, method_name):
#         return Request(self, method_name)
#
#     def __call__(self, method_name, **method_kwargs):
#         return getattr(self, method_name)(**method_kwargs)
#
#
# class Request(object):
#     __slots__ = ('_api', '_method_name', '_method_args')
#
#     def __init__(self, api, method_name):
#         self._api = api
#         self._method_name = method_name
#
#     def __getattr__(self, method_name):
#         return Request(self._api, self._method_name + '.' + method_name)
#
#     def __call__(self, **method_args):
#         self._method_args = method_args
#         return self.make_request()
#
#     def make_request(self):
#         return "123"


#
# from xmlrpc.client import ServerProxy
#
#
#
# server = ServerProxy("http://megu:min@meguminbot.ru:9001/RPC2")
# print(server.supervisor.getState())







# print(f" locals = {locals()}")
# print(f" locals = {globals()}")
#
# ldict = {}
# exec("a=3", globals(), ldict)
# a = ldict['a']
# print(a)
#
# print(f" locals = {locals()}")
# print(f" locals = {globals()}")




import copy
test_1 = [1, 2, 3, [1, 2, 3]]
test_copy = copy.copy(test_1)
print(test_1, test_copy)
test_copy[3].append(4)
print(test_1, test_copy)
test_1 = [1, 2, 3, [1, 2, 3]]
test_deepcopy = copy.deepcopy(test_1)
test_deepcopy[3].append(4)
print(test_1, test_deepcopy)

