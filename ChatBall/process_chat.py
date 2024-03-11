
import re
import pandas as pd
import time 
import matplotlib.pyplot as plt 
import matplotlib as mpl
import seaborn as sns
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


        return TotalMessages, chatusers, NoOfMessages 
    
    def barChartTotal(self, dataframe): 
        TotalMessages, chatusers, NoOfMessages = self.overallMetrics(dataframe)
        mpl.font_manager.FontProperties(fname=mpl.get_cachedir() + '/Humor-Sans.ttf')
        mpl.font_manager.FontProperties(fname=mpl.get_cachedir() + '/xkcd-script.ttf')
        if len(chatusers) > 4: 
            with plt.xkcd():
                fig, ax = plt.subplots(figsize=(16, 12))
                # Specify a font that includes the required glyphs
                ax.stem(chatusers, NoOfMessages, label=chatusers)
                ax.set_title('Breakdown of messages sent', fontfamily='Humor Sans')
                ax.set_ylabel('Number of messages', fontfamily='Humor Sans')
                ax.set_xlabel('Users', fontfamily='Humor Sans')
                plt.xticks(fontfamily='Humor Sans')
                plt.yticks(fontfamily='Humor Sans')
        else: 
            with plt.xkcd():
                fig, ax = plt.subplots(figsize=(10, 8))
                # Specify a font that includes the required glyphs
                ax.bar(chatusers, NoOfMessages, label=chatusers)
                ax.set_title('Breakdown of messages sent', fontfamily='Humor Sans')
                ax.set_ylabel('Number of messages', fontfamily='Humor Sans')
                ax.set_xlabel('Users', fontfamily='Humor Sans')
                plt.xticks(fontfamily='Humor Sans')
                plt.yticks(fontfamily='Humor Sans')

        plt.show()

    def messagesBreakdown(self, dataframe, year, breakdown_unit='day'):
        year_filter = (dataframe['Year'] == year)
        fdataframe_year = dataframe[year_filter]
        if len(fdataframe_year) != 0: 
            if breakdown_unit == 'day': 
                col = 'Day_Of_Year'
            elif breakdown_unit == 'month': 
                col = 'Month'
            elif breakdown_unit == 'week': 
                col = 'Day_Of_Week'
            else: 
                return "Enter a valid entry for the breakdown unit."
            start = min(fdataframe_year[col])
            end = max(fdataframe_year[col])

            users = fdataframe_year['User'].unique().tolist()

            messagesPerUnit = {} 
            for user in users: 
                messagesPerUnit[user] = []
            messagesPerUnit['Total'] = []
            messagesPerUnit['Unit'] = []

            for val in range(start, end+1):
                val_filter = (fdataframe_year[col] == val)
                fdataframe_unit = fdataframe_year[val_filter]
                messagesPerUnit['Unit'].append(val)
                TotalMessages = 0

                if len(fdataframe_unit) != 0:
                    for user in users: 
                        user_filter = (fdataframe_unit['User'] == user)
                        fdataframe_user = fdataframe_unit[user_filter]
                        messagesPerUnit[user].append(fdataframe_user.shape[0])
                        TotalMessages += fdataframe_user.shape[0]
                    messagesPerUnit['Total'].append(TotalMessages)
                else: 
                    for user in users: 
                        messagesPerUnit[user].append(0)
                    messagesPerUnit['Total'].append(0)

            return messagesPerUnit, breakdown_unit
        else: 
            return "No messages sent in {}".format(year)
        
    def dayToDate(self, day, year): 
        form = '%j %Y'
        date = time.strptime("{} {}".format(day, year), form)

        day_converted = date.tm_mday
        month = date.tm_mon
        converted_date = "{}/{}/{}".format(day_converted, month, year)

        return converted_date

    def plotByTime(self, dataframe, year, time_unit='day'): 
        bdict, _  = self.messagesBreakdown(dataframe, year, breakdown_unit=time_unit)
        plt.rcParams['font.family'] = 'Humor Sans'
        fig, axs = plt.subplots(1, 2, figsize=(12, 10))

        x = bdict['Unit']

        for key in bdict: 
            if (key == 'Unit') or (key == 'Total'): 
                pass
            else:
                with plt.xkcd(): 
                    axs[0].plot(x, bdict[key], '--', label=key) 
        
        axs[0].set_title('Messages sent per {} in {}'.format(time_unit, year))
        axs[0].set_xlabel('{} of the year'.format(time_unit))
        axs[0].set_ylabel('Number of messages')
        axs[0].legend()
        axs[0].grid()

        TotalMessages = bdict['Total']
        cum_total = [TotalMessages[0]]
        
        for i in range(1, len(TotalMessages)): 
            cum_sum = TotalMessages[i] + cum_total[-1]
            cum_total.append(cum_sum)

        axs[1].plot(x, cum_total, 'g--x')
        axs[1].set_title('Total messages sent per {} in {}'.format(time_unit, year))
        axs[1].set_xlabel('{} of the year'.format(time_unit))
        axs[1].set_ylabel('Number of messages')
        axs[1].grid()

        plt.show()

        return bdict
    

    




