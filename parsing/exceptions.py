class StopParsingError(Exception):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __str__(self):
            return super().__str__()

class BrokenAccountError(Exception):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __str__(self):
            return super().__str__()

class VkApiError(Exception):
    pass

class ApiError(VkApiError):

    def __init__(self, vk, method, values, error):
        super(ApiError, self).__init__()

        self.vk = vk
        self.method = method
        self.values = values
        self.code = error['error_code']
        self.error = error

    def __str__(self):
        return '[{}] {}'.format(self.code, self.error['error_msg'])

class ApiHttpError(VkApiError):

    def __init__(self, vk, method, values, response):
        super(ApiHttpError, self).__init__()
        self.vk = vk
        self.method = method
        self.values = values
        self.response = response

        return self.vk.method(self.method, self.values, raw=self.raw)

    def __str__(self):
        return 'Http error, response code {}'.format(self.response.status_code)
