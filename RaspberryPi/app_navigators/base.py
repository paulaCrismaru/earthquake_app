import time


class BaseNavigator:
    connect_url = "/connect"
    send_credentials = "/send-credentials"
    click_login = "/click-login"
    accept_authorization_url = "/accept-authorization"
    deny_authorization_url = "/deny-authorization"
    login_app_button = "button"

    def get_class_variables(self):
        return [item for item in dir(self)
                if not item.startswith('__') and
                item not in self.__dict__ and
                not callable(getattr(self, item))]



