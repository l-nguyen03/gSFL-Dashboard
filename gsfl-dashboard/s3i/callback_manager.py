import asyncio
from typing import Dict, Tuple, List, Any, Awaitable, Callable

from websocket import send

from s3i.logger import APP_LOGGER
MsgCallbackType = Callable[[Dict[str, Any]], Awaitable[None]]

class CallbackManager(object):
    """
    Global callback system, which is aimed at to be a single place to manage callbacks and process them
    """
    CALLBACK = 'callback'
    ONE_SHOT = 'one_shot'
    IS_ASYNC_CALLBACK = 'is_async_callback'
    ARGS = 'args'
    KWARGS = 'kwargs'

    def __init__(self):
        """
        Create an instance of the CallbackManager
        """
        self._stack = {}
        self.__message_callbacks: Dict[Tuple[str, str, str, str], List[Tuple[MsgCallbackType, bool]]] = {("", "", "", ""): []}
        self.logger = APP_LOGGER

    def add(self, prefix, callback, one_shot, is_async, *args, **kwargs):
        # prepare the stack
        if prefix not in self._stack:
            self._stack[prefix] = []

        if not isinstance(one_shot, bool):
            raise TypeError
        if not isinstance(is_async, bool):
            raise TypeError

        # create callback dictionary
        callback_dict = self.create_callback_dict(
            callback,
            one_shot,
            is_async,
            *args,
            **kwargs
        )

        # check for a duplicate
        if callback_dict in self._stack[prefix]:
            return prefix

        # append
        self._stack[prefix].append(callback_dict)
        return prefix

    def remove(self, prefix, callback_dict):
        if prefix not in self._stack:
            return False
        for callback in self._stack[prefix]:
            if callback == callback_dict:
                self._stack[prefix].remove(callback)
                return True
        return False

    def clear(self):
        if self._stack:
            self._stack = {}

    def process(self, prefix, loop=asyncio.get_event_loop()):
        if prefix not in self._stack:
            return False

        for callback_dict in self._stack[prefix]:
            method = callback_dict[self.CALLBACK]
            args = callback_dict[self.ARGS]
            kwargs = callback_dict[self.KWARGS]
            if callback_dict[self.IS_ASYNC_CALLBACK]:
                loop.create_task(method(*args, **kwargs))
            else:
                method(*args, **kwargs)

        remove = [callback_dict for callback_dict in self._stack[prefix] if callback_dict[self.ONE_SHOT]]
        for callback_dict in remove:
            self.remove(prefix, callback_dict)

        return True

    def create_callback_dict(self, callback, one_shot, is_async, *args, **kwargs):
        """
        Create and return callback dictionary

        :param method callback:
        :param bool one_shot:
        :param is_async:
        :return:
        """

        return {
            self.CALLBACK: callback,
            self.ONE_SHOT: one_shot,
            self.IS_ASYNC_CALLBACK: is_async,
            self.ARGS: args,
            self.KWARGS: kwargs
        }

    def add_message_callback(
            self,
            callback: MsgCallbackType,
            sender_id: str = "",
            receiver_id: str = "",
            message_type: str = "",
            replying_to_msg: str = "",
            is_oneshot: bool = False
    ) -> None:
        """use empty str as wildcard for sender, receiver and message_type"""
        if (sender_id, receiver_id, message_type, replying_to_msg) not in self.__message_callbacks:
            self.__message_callbacks[(sender_id, receiver_id, message_type, replying_to_msg)] = []
        self.__message_callbacks[(sender_id, receiver_id, message_type, replying_to_msg)].append((callback, is_oneshot))

    def remove_message_callback(
            self,
            callback: MsgCallbackType,
            sender_id: str = "",
            receiver_id: str = "",
            message_type: str = "",
            replying_to_msg: str = "",
            is_oneshot: bool = False
    ) -> None:
        """use empty str as wildcard for sender, receiver and message_type"""
        if (sender_id, receiver_id, message_type, replying_to_msg) in self.__message_callbacks:
            self.__message_callbacks[(sender_id, receiver_id, message_type, replying_to_msg)].remove((callback, is_oneshot))
            if len(self.__message_callbacks[(sender_id, receiver_id, message_type, replying_to_msg)]) == 0:
                self.__message_callbacks.pop((sender_id, receiver_id, message_type, replying_to_msg))

    @staticmethod
    def __check_filter(msg_filter: Tuple[str, ...], val: Tuple[str, ...]) -> bool:
        """checks if val fits filter, empty string as wildcard"""
        if len(msg_filter) != len(val):
            raise ValueError("length of filter != length of value")
        for i in range(len(msg_filter)):
            if msg_filter[i] != "":
                if msg_filter[i] != val[i]:
                    return False
        return True

    def process_message(self, message: Dict[str, Any], loop=None):
        replying_to_msg = ""
        sender_id = ""
        receiver_id = ""
        message_type = ""
        try:
            sender_id = message["sender"]
            receiver_ids = message["receivers"]
            message_type = message["messageType"]
            if "replying_to_msg" in message:
                replying_to_msg = message["replying_to_msg"]
            message_signatures = [(sender_id, r_id, message_type, replying_to_msg) for r_id in receiver_ids]
        except KeyError as e:
            self.logger.error(f"Keyerror accessing message for callback filter, message: {message}, error: {e} ")
            return
        if loop is None:
            loop = asyncio.get_running_loop()
        for msg_filter, method_list in self.__message_callbacks.items():
            for signature in message_signatures:
                if self.__check_filter(msg_filter, signature):
                    for method, is_oneshot in method_list:
                        try:
                            loop.create_task(method(message))
                        except:
                            self.logger.error(f"unexpected error trying to create callback task for message {message}")
                        if is_oneshot:
                            self.remove_message_callback(
                                callback=method,
                                sender_id=sender_id,
                                receiver_id=receiver_id,
                                message_type=message_type,
                                is_oneshot=is_oneshot
                            )

