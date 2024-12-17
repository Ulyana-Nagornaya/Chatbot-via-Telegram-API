class Token:
    def __init__(self):
        self.token = '' #input your token here
        self.name = 'hsetuberous_bot'
    def get_token(self):
        return self.token
    
token = Token().get_token()
print(token)