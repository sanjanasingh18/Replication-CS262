
class ClientAction:
    def __init__(self,
                 action,
                 client_username='',
                 password='',
                 recipient_username='',
                 message='',
                 available_messages=''):
        self.action = action
        self.client_username = client_username
        self.password = password
        self.recipient_username = recipient_username
        self.message = message
        self.available_messages = available_messages

    def setAction(self, action):
        self.action = action

    def setClientUsername(self, client_username):
        self.client_username = client_username

    def setPassword(self, password):
        self.password = password

    def setRecipientUsername(self, recipient_username):
        self.recipient_username = recipient_username

    def setMessages(self, message):
        self.message = message

    def setAvailableMessages(self, available_messages):
        self.available_messages = available_messages

    def getAction(self, action):
        return self.action

    def getClientUsername(self, client_username):
        return self.client_username

    def getPassword(self, password):
        return self.password

    def getRecipientUsername(self, recipient_username):
        self.recipient_username = recipient_username

    def getMessages(self, message):
        return self.message

    def getAvailableMessages(self, available_messages):
        return self.available_messages

    def exportAction(self):
        message = self.action + "we_hate_cs262" +\
            self.client_username + "we_hate_cs262" +\
            self.password + "we_hate_cs262" +\
            self.recipient_username + "we_hate_cs262" +\
            self.message + "we_hate_cs262" +\
            self.available_messages

        return message
