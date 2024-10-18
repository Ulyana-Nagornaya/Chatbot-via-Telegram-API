class Token:
    def __init__(self):
        self.token = '7604474051:AAErnNbDz427QWCrT4IBl039aCebdZx17fM'
        self.name = 'hsetuberous_bot'
    def get_token(self):
        return self.token
    
token = Token().get_token()
print(token)