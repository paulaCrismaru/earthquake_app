from base import BaseNavigator
import time


class DropboxNavigator(BaseNavigator):
    name = "dropbox"

    service_auth_url = "https://www.dropbox.com/1/oauth2/authorize?"
    service_auth_cookie = "cookie_notif"
    service_login_form_css_selector = ".clearfix.credentials-form.login-form"
    service_email_field_name = "login_email"
    service_email_field_css_selector = ".text-input-input.autofocus"
    service_password_field_name = "login_password"
    service_password_field_css_selector = ".password-input.text-input-input"
    service_login_button_css_selector = ".login-button.button-primary"
    service_authorize_form_id = "regular-login-forms"
    service_allow_button_name = "allow_access"
    service_deny_button_name = "deny_access"
    service_authorize_box_id = "auth"

    def __init__(self, browser):
        self.browser = browser
        base = BaseNavigator()
        for variable_name in base.get_class_variables():
            if variable_name == "login_app_button":
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name.title())
            else:
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name)
            setattr(DropboxNavigator, variable_name, variable_value)

    def do_login_service(self, email, password):
        self.insert_in_login_field(
            self.service_authorize_form_id,
            self.service_email_field_css_selector,
            self.service_email_field_name, email)
        self.insert_in_login_field(
            self.service_authorize_form_id,
            self.service_password_field_css_selector,
            self.service_password_field_name, password)
        return ['login']

    def insert_in_login_field(self, form_id, field_css_selector, field_name, data):
        form = self.browser.find_element_by_id(form_id)
        elements = form.find_elements_by_css_selector(field_css_selector)
        for element in elements:
            if element.get_attribute("name") == field_name:
                element.clear()
                element.send_keys(data)
                return

    def click_login_service(self):
        form = self.browser.find_element_by_css_selector(self.service_login_form_css_selector)
        button = form.find_element_by_css_selector(self.service_login_button_css_selector)
        button.click()
        return ["allow", "deny"]

    def accept_authorization(self):
        try:
            self.click_button(self.service_authorize_box_id, self.service_allow_button_name)
        except:
            raise

    def deny_authorization(self):
        try:
            self.click_button(
                self.service_authorize_box_id,
                self.service_deny_button_name)
        except:
            raise

    def click_button(self, form_id, button_name):
        try:
            form = self.browser.find_element_by_id(form_id)
            button = form.find_element_by_name(button_name)
            button.click()
        except:
            raise

    def click_login_button_app(self):
        try:
            elements = self.browser.find_elements_by_id(self.login_app_button)
            elements[0].click()
        except:
            raise

    def is_redirect(self):
        time.sleep(1)
        if self.browser.current_url.encode('utf-8').startswith(self.service_auth_url):
            if self.browser.get_cookie(self.service_auth_cookie) is not None:
                return ['accept', 'decline'], None
            else:
                return ['sign-in'], ['email', 'password']
        return None, None