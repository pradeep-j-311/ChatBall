
import re
import pandas as pd
import time 
import matplotlib.pyplot as plt 
from datetime import timedelta
import click 
from flask import current_app, g

def init_chat(): 
    chat = whatsAppChat(path=None)

@click.command('init-chat')
def init_chat_command(): 
    init_chat()
    click.echo('Chat initialised')

def init_app(app): 
    app.cli.add_command(init_chat_command)

class whatsAppChat: 

    def __init__(self, path):
        self.chat_path = path
        self.whatAppTimeFormat = '[%d/%m/%y, %H:%M:%S]'

    def chat_to_df(self): 
        with open(self.chat_path, encoding='utf-8') as f: 
            chat = f.read()
            messages = chat.split('\n') # create a list out of the chat history 

        # remove date/time 
        DateTime, DateTimeObject, gmTime, month, day, year, hour, minute, second, days_since, hours_since, minutes_since, seconds_since, wDay, yDay, Users, Contents = self.extractInfo(messages)
        data = {
            "DateTime": DateTime, 
            "DateTimeObject": DateTimeObject, 
            "gmTime": gmTime, 
            "Month": month, 
            "Day": day,
            "Year": year, 
            "Hour": hour, 
            "Minute": minute, 
            "Seconds": second,
            "DaysSince": days_since,
            "HoursSince": hours_since, 
            "MinutesSince": minutes_since, 
            "SecondsSince": seconds_since,
            "Day_Of_Week": wDay, 
            "Day_Of_Year": yDay,
            "User": Users, 
            "Message": Contents
        }
        chat_df = pd.DataFrame(data)

        return chat_df

    def extractInfo(self, messages): 

        dt = re.compile(r'\[[0-9]*/[0-9]*/[0-9]*, [0-9]*:[0-9]*:[0-9]*\]') # regex expression for extracting the date and time 
        message_dt = [] # intialise list to store date and time 
        month = []
        day = []
        day_of_week = []
        hour = []
        minute = []
        year = []
        seconds = []
        day_of_year = []
        message_dt_converted = []
        time_delta = []
        Users = []
        Contents = []
        elapsed_d = []
        elapsed_h = []
        elapsed_m = []
        elapsed_s = []
        gmTime = []

        
        # extract raw date/time values 
        for message in messages: 
            current_date = dt.search(message)
            if current_date != None: 
                extracted_date = current_date.group()
                message_dt.append(extracted_date)

                converted_date = time.strptime(extracted_date, self.whatAppTimeFormat)
                gmTime.append(time.mktime(converted_date))
                if len(time_delta) == 0: 
                    time_delta.append(0)
                    elapsed_d.append(0)
                    elapsed_h.append(0)
                    elapsed_m.append(0)
                    elapsed_s.append(0)
                else: 
                    elapsed_time = time.mktime(converted_date) - time.mktime(message_dt_converted[-1])
                    el_d, el_h, el_m, el_s = self.processElapsedTime(elapsed_time)
                    elapsed_d.append(el_d)
                    elapsed_h.append(el_h)
                    elapsed_m.append(el_m)
                    elapsed_s.append(el_s)
                
                message_dt_converted.append(converted_date)
                month.append(converted_date.tm_mon)
                day.append(converted_date.tm_mday)
                day_of_week.append(converted_date.tm_wday)
                hour.append(converted_date.tm_hour)
                minute.append(converted_date.tm_min)
                year.append(converted_date.tm_year)
                seconds.append(converted_date.tm_sec)
                day_of_year.append(converted_date.tm_yday)
                # after the date/time has been extracted we remove it from the message line 
                clean_message = dt.sub("", message)
                user_content_split = re.split(':', clean_message, 1)
                user = re.sub('\\u200e', '', user_content_split[0])
                content = user_content_split[1]

                Users.append(user)
                Contents.append(content)

            else: 
                # the way whatsapp exports message means that if a subsequent message is sent by the same user at a close enough time stamp then the data-time is not present
                # in that line. For this we simply add the previous date/time to the message with this information missing
                message_dt.append(message_dt[-1])
                message_dt_converted.append(message_dt_converted[-1])
                gmTime.append(gmTime[-1])
                month.append(month[-1])
                day.append(day[-1])
                day_of_week.append(day_of_week[-1])
                hour.append(hour[-1])
                minute.append(minute[-1])
                year.append(year[-1])
                seconds.append(seconds[-1])
                day_of_year.append(day_of_year[-1])

                Users.append(Users[-1])
                Contents.append(message)
                
                elapsed_d.append(0)
                elapsed_h.append(0)
                elapsed_m.append(0)
                elapsed_s.append(0)

        return message_dt, message_dt_converted, gmTime, month, day, year, hour, minute, seconds, elapsed_d, elapsed_h, elapsed_m, elapsed_s, day_of_week, day_of_year, Users, Contents
    
    def processElapsedTime(self, elapsed): 
        daySeconds = 60*60*24
        hourSeconds = 60*60
        minuteSeconds = 60

        elapsed_days = elapsed // daySeconds 
        elapsed_seconds = elapsed % daySeconds
        elapsed_hours = elapsed_seconds // hourSeconds
        elapsed_seconds %= hourSeconds
        elapsed_minutes = elapsed_seconds // minuteSeconds
        elapsed_seconds %= minuteSeconds

        return elapsed_days, elapsed_hours, elapsed_minutes, elapsed_seconds 
    
    def overallMetrics(self, dataframe): 

        TotalMessages = len(dataframe)
        chatusers = dataframe['User'].unique() 
        NoOfMessages = []

        for user in chatusers: 
            nMessages = dataframe['User'].value_counts()[user]
            NoOfMessages.append(nMessages)


        return TotalMessages, NoOfMessages 
