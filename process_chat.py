import re
import pandas as pd

class whatsAppChat: 

    def __init__(self, path):
        self.chat_path = path

    def chat_to_df(self): 
        with open(self.chat_path, encoding='utf-8') as f: 
            chat = f.read()
            messages = chat.split('\n') # create a list out of the chat history 

        # remove date/time 
        messages_woDateTime , DateTime = self.extractDateTime(messages)
        # remove username
        Content, Users = self.extractUsers(messages_woDateTime)
        cols = [DateTime, Users, Content]
        chat_df = pd.DataFrame(cols, columns=['DateTime', 'User', 'Message Content'])

        return chat_df

    def extractDateTime(self, messages): 

        dt = re.compile(r'\[[0-9]*/[0-9]*/[0-9]*, [0-9]*:[0-9]*:[0-9]*\]') # regex expression for extracting the date and time 
        message_dt = [] # intialise list to store date and time 
        cleaned_messages = []

        for message in messages: 
            current_date = dt.search(message)
            if current_date != None: 
                message_dt.append(current_date.group())
                previous_date = current_date
                # after the date/time has been extracted we remove it from the message line 
                clean_message = dt.sub("", message)
                cleaned_messages.append(clean_message)
            else: 
                # the way whatsapp exports message means that if a subsequent message is sent by the same user at a close enough time stamp then the data-time is not present
                # in that line. For this we simply add the previous date/time to the message with this information missing
                message_dt.append(previous_date.group())
                cleaned_messages.append(message)

        return cleaned_messages, message_dt 

    def extractUsers(self, messages): 
        cleaned_messages = [] 
        message_users = []
        for message in messages: 
            # in whatsapp chat history export the users and the message content are seperated by ":"
            # eg: Vidhi: Hello! 
            # Name should not contain the ":" character 
            current_split = re.split(":", message, 1)
            if len(current_split) > 1: 
                message_users.append(current_split[0])
                cleaned_messages.append(current_split[1])
                previous_user = current_split[0]
            else: 
                cleaned_messages.append(current_split[0])
                message_users.append(previous_user)

        return cleaned_messages, message_users 
    
    def noOfMessages(self, dataframe): 
        
        TotalMessages = len(dataframe)
        
        return TotalMessages