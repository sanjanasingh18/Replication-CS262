
class ClientAction:
    def __init__(self,
                 action,
                 client_username='',
                 password='',
                 logged_in='',
                 recipient_username='',
                 current_messages='',
                 available_messages=''):
        self.action = action.lower()
        self.client_username = client_username
        self.password = password
        self.logged_in = logged_in.lower()
        self.recipient_username = recipient_username
        self.current_messages = current_messages
        self.available_messages = available_messages

    def setAction(self, action):
        self.action = action

    def setClientUsername(self, client_username):
        self.client_username = client_username

    def setPassword(self, password):
        self.password = password

    def setLoggedIn(self, logged_in):
        self.logged_in = logged_in

    def setRecipientUsername(self, recipient_username):
        self.recipient_username = recipient_username

    def setCurrentMessages(self, current_messages):
        self.current_messages = current_messages

    def setAvailableMessages(self, available_messages):
        self.available_messages = available_messages

    def getAction(self):
        return self.action

    def getClientUsername(self):
        return self.client_username

    def getPassword(self):
        return self.password

    def getLoggedIn(self):
        return self.logged_in

    def getRecipientUsername(self):
        return self.recipient_username

    def getCurrentMessages(self):
        return self.current_messages

    def getAvailableMessages(self):
        return self.available_messages

    def exportAction(self):
        message = self.action + "we_hate_cs262" +\
            self.client_username + "we_hate_cs262" +\
            self.password + "we_hate_cs262" +\
            self.logged_in + "we_hate_cs262" +\
            self.recipient_username + "we_hate_cs262" +\
            self.current_messages + "we_hate_cs262" +\
            self.available_messages

        return message
