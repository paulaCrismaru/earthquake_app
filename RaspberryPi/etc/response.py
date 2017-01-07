class Response:
    def __init__(self, code, current_page, buttons, fields, message=None):
        self.code = code
        self.current_page = current_page
        self.buttons = buttons
        self.fields = fields
        self.message = message
