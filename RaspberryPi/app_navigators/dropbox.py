import time


class DropboxNavigator:
    name = "dropbox"

    # app parameters
    connect_url = "/connect-dropbox"
    send_credentials = "/send-dropbox-credentials"
    click_login = "/click-login-dropbox"
    accept_authorization = "/accept-dropbox"
    deny_authorization = "/deny-dropbox"
    app_login_button_id = "Dropbox-button"

    # service parameters
    login_app_button = "Dropbox-button"
    service_auth_url = "https://www.dropbox.com/1/oauth2/authorize?"
    service_auth_cookie = "cookie_notif"
    service_login_form_css_selector = ".clearfix.credentials-form.login-form"
    service_email_field_name = "login_email"
    service_email_field_css_selector = ".text-input-input.autofocus"
    service_password_field_name = "login_password"
    service_password_field_css_selector = ".password-input.text-input-input"
    service_login_button_css_selector = ".login-button.button-primary"
    service_authorize_form_id = "authorize-form"
    service_allow_button_css_selector = ".auth-button.button-primary"
    service_deny_button_name = "deny_access"

    def __init__(self, browser):
        self.browser = browser

    def click_login_button_app(self):
        elements = self.browser.find_elements_by_id(self.app_login_button_id)
        elements[0].click()

    def is_redirect(self):
        time.sleep(1)
        if self.browser.current_url.encode('utf-8').startswith():
            if self.browser.get_cookie(self.service_auth_cookie) is not None:
                return ['accept', 'decline']
            else:
                return ['email', 'password']

    def do_login_service(self, email, password):
        self.insert_in_login_field(self.service_email_field_css_selector,
                                   self.service_email_field_name, email)
        self.insert_in_login_field(self.service_password_field_css_selector,
                                   self.service_password_field_name, password)

    def insert_in_login_field(self, field_css_selector, field_name, data):
        form = self.browser.find_element_by_css_selector(self.service_login_form_css_selector)
        elements = form.find_elements_by_css_selector(field_css_selector)
        for element in elements:
            if element.get_attribute("name") == field_name:
                element.send_keys(data)
                return

    def click_login_service(self):
        form = self.browser.find_element_by_css_selector(self.service_login_form_css_selector)
        button = form.find_element_by_css_selector(self.service_login_button_css_selector)
        button.click()

    def accept_authorization(self):
        form = self.browser.find_element_by_id(self.service_authorize_form_id)
        allow = form.find_element_by_css_selector(self.service_allow_button_css_selector)
        allow.click()

    def deny_autorization(self):
        self.click_button(self.service_login_form_css_selector, self.service_deny_button_name)

    def click_button(self, form_css, button_name):
        form = self.browser.find_element_by_css_selector(form_css)
        button = form.find_element_by_name(button_name)
        button.click()