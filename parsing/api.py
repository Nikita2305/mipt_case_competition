import requests
import json
import threading
from .exceptions import *
import time

class RaribleApi:
    
    def __init__(self, DELAY, api_v=""): # -staging, -dev
        self.lock = threading.Lock()
        self.last_request = 0.0
        self.DELAY = DELAY
        self.api_v = api_v

    def method(self, method, params={}, print_query=False):
        """ Вызов метода API

        :param method: Название метода
        :type method: str
        
        :param params: Параметры
        :type params: dict

        Бросает `ApiHttpError` в случае неуспешного кода возварата http запроса
        
        Бросает `ApiError` в случае неуспешного запроса к API

        Возвращает `response['response']` в случае успеха
        """

        params = params.copy() if params else {}

        with self.lock:
            # Ограничение запросов в секунду
            delay = self.DELAY - (time.time() - self.last_request)

            if delay > 0:
                time.sleep(delay)

            query = f"https://api{self.api_v}.rarible.org/v0.1/{method}"

            if (print_query):
                print(query, params)

            response = requests.get(
                query, 
                params=params
            )

            self.last_request = time.time() 

        if response.ok:
            response = response.json()
        else:
            raise ApiHttpError(self, method, params, response)

        return response
