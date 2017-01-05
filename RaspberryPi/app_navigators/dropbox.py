import time


class DropboxNavigator:
    name = "dropbox"
    connect_url = "/connect-dropbox"
    send_credentials = "/send-dropbox-credentials"
    click_login = "/click-login-dropbox"
    accept_authorization = "/accept-dropbox"
    deny_authorization = "/deny-dropbox"

    def __init__(self, browser):
        self.browser = browser

    def click_login_button_app(self):
        elements = self.browser.find_elements_by_id("Dropbox-button")
        elements[0].click()

    def is_redirect(self):
        time.sleep(1)
        if self.browser.current_url.encode('utf-8').startswith("https://www.dropbox.com/1/oauth2/authorize?"):
            if self.browser.get_cookie("cookie_notif") is not None:
                return ['accept', 'decline']
            else:
                return ['email', 'password']

    def do_login_service(self, email, password):
        form = self.browser.find_element_by_css_selector(".clearfix.credentials-form.login-form")
        elements = form.find_elements_by_css_selector(".text-input-input.autofocus")
        for element in elements:
            if element.get_attribute("name") == "login_email":
                element.send_keys(email)
                break
        elements = form.find_elements_by_css_selector(".password-input.text-input-input")
        for element in elements:
            if element.get_attribute("name") == "login_password":
                element.send_keys(password)
                break

    def click_login_service(self):
        form = self.browser.find_element_by_css_selector(".clearfix.credentials-form.login-form")
        button = form.find_element_by_css_selector(".login-button.button-primary")
        button.click()

    def accept_authorization(self):
        form = self.browser.find_element_by_id("authorize-form")
        allow = form.find_element_by_css_selector(".auth-button.button-primary")
        allow.click()

    def deny_autorization(self):
        form = self.browser.find_element_by_css_selector(".clearfix.credentials-form.login-form")
        deny = form.find_element_by_name("deny_access")
        deny.click()