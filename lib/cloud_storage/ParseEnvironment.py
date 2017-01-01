class Parser:
    def __init__(self):
        file = open('./creds.env', 'r')
        for item in file:
            setattr(Parser, item.split("=")[0], item.split("=")[1])