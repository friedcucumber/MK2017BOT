#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import telebot
import config
import time
import os
import datetime
import logging
import utils
import random
import sqlite3
#import SQLighter

from telebot import types

codes=['орел', 'персик', 'пупок','мокруха']
questions=['сладкий фрукт?','что находится в середине тела?','убийство']
hints=[['соседняя область', 'птица такая есть','орел, тупой что ли?'],['есть такая картина','Эй, ты просто ******'],['смотри, чтобы не развязался'],['на жаргоне думай','очень влажно']]


bot = telebot.TeleBot(config.token)
user_dict = {}

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_all(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Players').fetchall()

    def select_single(self, rownum):
        """ Получаем одну строку с номером rownum """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Players WHERE id = ?', (rownum,)).fetchall()[0]

    def count_rows(self):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM Players').fetchall()
            return len(result)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()


class User:
    def __init__(self, name):
        self.name = name
        self.team = None

@bot.message_handler(commands=['testmusic'])
def send_music(message, name):
    for file in os.listdir('media/'):
        if file.split(name+'.')[-1] == 'ogg':
            f = open('media/'+file, 'rb')
            res = bot.send_voice(message.chat.id, f, None)
            print(res)
        time.sleep(2)

@bot.message_handler(commands=['testpicture'])
def send_picture(message, name):
    for file in os.listdir('media/'):
        if file.split(name+'.')[-1] == 'jpg':
            f = open('media/'+file, 'rb')
            res = bot.send_photo(message.chat.id, f, None)
            print(res)
        time.sleep(2)
        
@bot.message_handler(commands=['game'])
def game(message):
    # Подключаемся к БД
    db_worker = SQLighter(config.database_name)
    # Получаем случайную строку из БД
    #row = db_worker.select_single(random.randint(1, utils.get_rows_count()))
    row = db_worker.select_single(2)
    # Формируем разметку
    markup = utils.generate_markup(row[1], row[2])
    # Отправляем аудиофайл с вариантами ответа
    bot.send_message(message.chat.id, row[1]+' '+str(row[2]))
    # Включаем "игровой режим"
   #utils.set_user_game(message.chat.id, row[2])
    # Отсоединяемся от БД
    db_worker.close()

    
# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    chat_id = message.chat.id
    global hintcount
    hintcount =0
    global codeindex
    codeindex = 0
    global currentquestion
    currentquestion = 0
    global starttime
    starttime=message.date
    msg = bot.send_message(chat_id, """\
Добрый день!
Как тебя зовут?
""")
    bot.register_next_step_handler(msg, process_team_step)

def process_team_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Кирилл', 'Максим')
        msg = bot.send_message(chat_id, 'Кто твой руководитель?', reply_markup=markup)
       # msg = bot.send_message(chat_id, config.database_name)
        bot.register_next_step_handler(msg, process_choose_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_choose_step(message):
    try:
        chat_id = message.chat.id
        team = message.text
        user = user_dict[chat_id]
        if (team == u'Кирилл') or (team == u'Максим'):
            user.team = team
        else:
            raise Exception()
        bot.send_message(chat_id, 'Удачной игры ' + user.name + '\nТы в команде:' + user.team)        
        bot.send_message(chat_id, "Вопрос #1: Город южнее тулы")        
    except Exception as e:
        bot.reply_to(message, 'oooops')

@bot.message_handler(commands=['подсказка'])
def give_hint(message):
    global hintcount 
    hintnumber=len(hints[currentquestion])
    if 0 < (len(hints[currentquestion])-hintcount) <= hintnumber:
        msg = bot.reply_to(message, "Первая подсказка:")
        #bot.send_message(message.chat.id, "codeindex")
        bot.send_message(message.chat.id, hints[currentquestion][hintcount])
        hintcount += 1
    else:
      #  bot.send_message(message.chat.id, "codeindexlen"+str(len(hints[codeindex][hintcount]))+"codeindex"+str(hints[codeindex][hintcount]))
        bot.send_message(message.chat.id, "Подсказки кончились!"+str(hintcount)+"из"+str(len(hints[currentquestion])))
        

def give_next_question(msg, code):
    global currentquestion
    global hintcount
    hintcount=0
    currentquestion +=1
    bot.send_message(msg.chat.id, "Следующий вопрос:"+str(questions[code])) 

#@bot.message_handler(commands=['код'])
@bot.message_handler(func=lambda message: message.text in codes)
def game(message):
    global currentquestion
    global codeindex
    global hintcount
    codeindex=codes.index(message.text)
    bot.send_message(message.chat.id, "Код №"+str(codeindex+1)+" принят!")
    if codeindex == 0:
        send_picture(message, 'photo')
        give_next_question(message, codeindex)
       #answerssum +=codeindex
        
#    questionindex=questions.index(codeindex)
    if codeindex == 1:
        send_music(message, 'song')
        give_next_question(message, codeindex)
        #answerssum +=codeindex
                                 
    if codeindex == 2:
        give_next_question(message, codeindex)
       # answerssum +=codeindex
        
    if codeindex == 3:
        hintcount=0
        currentquestion +=1
        #answerssum +=codeindex
        endtime=message.date-starttime
        bot.send_message(message.chat.id, "Конец игры! Ваше время "+time.strftime('%H:%M:%S', time.gmtime(endtime)))

    
       
#@bot.message_handler(func=lambda message: message.text not in codes)
#def now_answer(message):
#    global codeindex
#    codeindex=0 
#    hintcount=0    
#    bot.send_message(message.chat.id, "Код неверный")

#bot.polling()

if __name__ == '__main__':
    utils.count_rows()
    random.seed()
    bot.polling(none_stop=True)
