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

codes=['hafanana', 'тамагочи', 'тетрис','корольлев','писание','зачарованные','битлджус','198','150421042017']
questions=["""Задание 1.2
«Отлично!» - вопит Валдис! Валдис жмет вам руки, передает вам свои поздравления и привет тоже передает…и внезапно просит об услуге – его телефон разрядился, а ему нужно срочно покормить своего домовенка!
Примечание: Загадано точное место. 2ГИС в помощь). Звонить никуда не нужно) Код вы найдете на одном из фонарных столбов, около загаданного места.
Формат ответа: указан на листе в загаданном месте. 
""","""Задание 2
Покормив домовенка, вы услышали странный звук мотора, где-то у вас над головой!
Подняв глаза в небо, вы замечаете красную дымящуюся точку. Присмотревшись, вы понимаете, что это самолет ЯК, который терпит крушение над городом, с мая 1990 года.""","""Задание 3.1


Все смотрели этот мультик в детстве!) И в этом мультике была одна очень грустная сцена, которая никого не оставляла равнодушным. Наверняка и вы тоже плакали тогда…

Примечание: задание берется из машины, ехать никуда не нужно)

Формат ответа: 2 слова на русском, маленькими буквами без пробелов""", """Задание 3.2

А ведь в нашем городе тоже есть Лев, который идёт.. за водкой!)

Примечание: загадано конкретное место. Ищите слова под ногами.

Формат ответа: первое слово цитаты на русском, маленькими буквами, без пробелов.
""","""Задание 4.1

Вы услышали грохот над городом и таинственный голос прошептал:
«ЕНАОРЫАЗАЧНВ!»
«Что за белиберда!» - подумали вы.

Примечние: задание берется из машины, ехать никуда не нужно)

Формат ответа: слово на русском маленькими буквами.
""","""Задание 4.2

Так вот что за грохот вы слышали! Это бомбанул Валодин пердак после очередной игры в доту!
Прю Пайпер и Фиби попали в беду! Изучая книгу таинств, сестры произнесли какое-то заклинание и оказались в Туле! Да ещё и в прошлом! Последний раз их видели в этих местах:
""","""Задание 5


Вы спасли сестер! Самое время немного подкрепиться! Помните, как в детстве Вы хотели попасть  именно туда? А попав - попробовать хотелось ВСЁ! Но предпочтение в основном отдавалось именно определенной позиции в меню! Преодолев препятствие в виде длиннющие очереди и получив наконец заветный пакет с обедом вы стремились скорее развернуть его и узнать - что же досталось вам в этот раз, помимо булки с сыром, картошки и газировки?


Формат ответа: цифры""","""Задание 6.1

Подкрепились! Теперь пришло время...СПАСАТЬ МИР! 
С вами в машине присутствует агент под прикрытием, у которого в кармане есть билеты на планетарный круизный корабль-гранд-отель! 

Примечание: выдвигайтесь к планетарному круизному корабль-гранд-отелю! Для перехода на следующее задание поговорите с агентами. Не забудьте ваши билеты - без них вы не сможете попасть на корабль!
"""]
hints=[['соседняя область', 'птица такая есть','орел, тупой что ли?'],['есть такая картина','Эй, ты просто ******'],['смотри, чтобы не развязался'],['на жаргоне думай','очень влажно']]

#global gamestarted
#gamestarted=0

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
        
    def create_new_player(self, username, starttime):
        with self.connection:
            self.cursor.execute('INSERT INTO Players(Name, Time_Gaming) VALUES(?,?)', (username, starttime))
            self.cursor.execute('INSERT INTO Teams(Teammates) VALUES(?)', (username, ))
            
    def add_team(self, username, team):
        with self.connection:
           self.cursor.execute('UPDATE Players SET Team = ? WHERE Name = ?', (team, username))
           self.cursor.execute('UPDATE Teams SET TeamName = ? WHERE Teammates = ?', (team, username))
           
    def read_team_sql(self, username):
        with self.connection:
            return self.cursor.execute('SELECT Team FROM Players WHERE Name = ?', (username, )).fetchall()
           
    def show_teammates(self, teamname):
        with self.connection:
            return self.cursor.execute('SELECT Teammates FROM Teams WHERE TeamName = ?', [teamname]).fetchall()
            
    def player_exists(self, name):
        with self.connection:
           return self.cursor.execute('SELECT EXISTS(SELECT * FROM Players WHERE Name = ?)', (name,)).fetchall()
           
    def read_last_code(self, name):
        """ Получаем одну строку с номером rownum """
        with self.connection:
           return self.cursor.execute('SELECT Last_Answered_Question FROM Players WHERE Name = ?', (name,)).fetchall()
           # return self.cursor.execute('SELECT answered_code FROM Teams WHERE TeamName = ?', (teamname,)).fetchall()

    def write_last_code(self, code, name):
        """ Получаем одну строку с номером rownum """
        with self.connection:
            self.cursor.execute('UPDATE Players SET Last_Answered_Question = ? WHERE Name = ?', (code, name))
            self.cursor.execute('UPDATE Teams SET answered_code = ? WHERE Teammates = ?', (code, name))

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
        time.sleep(1)

@bot.message_handler(commands=['testpicture'])
def send_picture(message, name):
    for file in os.listdir('media/'):
        if file.split(name+'.')[-1] == 'jpg':
            f = open('media/'+file, 'rb')
            res = bot.send_photo(message.chat.id, f, None)
            print(res)
        time.sleep(1)


@bot.message_handler(commands=['testteam'])
def testteams(message):
    db_worker = SQLighter(config.database_name)
    name="Кирилл"
    #row=bot.send_message(message.chat.id, "1")
    #db_worker.show_teammates(name)
    teammates=str(db_worker.show_teammates(name))
    teammates=teammates.replace("(","")
    teammates=teammates.replace(")","")
    teammates=teammates.replace("\'","")
    bot.send_message(message.chat.id, teammates)
    db_worker.close()
    #bot.send_message(message.chat.id, "2")
    
    
    

        
#@bot.message_handler(commands=['game'])
def game(message):
    # Подключаемся к БД
    chat_id = message.chat.id
    user = user_dict[chat_id]
    db_worker = SQLighter(config.database_name)
    # Получаем случайную строку из БД
    #row = db_worker.select_single(random.randint(1, utils.get_rows_count()))
    team_name=user.team
    if team_name == "Максим":
        row = db_worker.select_single(2)
    if team_name =="Кирилл":
        row = db_worker.select_single(1)
    # Формируем разметку
    #markup = utils.generate_markup(row[1], row[2])
    # Отправляем тестовое сообщение
    bot.send_message(message.chat.id, row[1]+' '+str(row[2]))
    # Включаем "игровой режим"
   #utils.set_user_game(message.chat.id, row[2])
    # Отсоединяемся от БД
    db_worker.close()

def save_code_to_base (chatid, user, code):
    db_worker = SQLighter(config.database_name)
    chat_id = chatid
    #user = user_dict[chatid]
    #team_name=user.team
    #if team_name == "Максим":
    #bot.send_message(chat_id, str(code))
    db_worker.write_last_code(code, user)
    db_worker.close()
    #if team_name =="Кирилл":
   #     row = db_worker.select_single(user, code)
   
@bot.message_handler(commands=['jump'])
def read_code_from_base (message):
       chat_id = message.chat.id
       #user = user_dict[chat_id]
       #chat_id = message
       db_worker = SQLighter(config.database_name)
      # user = user_dict[message.chat.id]
       #name=db_worker.read_team_sql(message.from_user.username)
       #bot.send_message(chat_id, teamname)
       #if team_name == "Максим":
       row=db_worker.read_last_code(message.from_user.username)
       bot.send_message(chat_id, row)
       db_worker.close()

def create_new_player (chatid, username, starttime):
       #chat_id = message.chat.id
       #chat_id = message
       db_worker = SQLighter(config.database_name)
      # user = user_dict[message.chat.id]
       #team_name=user.team
       #if team_name == "Максим":
       db_worker.create_new_player(username, starttime)
       db_worker.close()
       
def add_team (username, team):
       #chat_id = message.chat.id
       #chat_id = message
       db_worker = SQLighter(config.database_name)
      # user = user_dict[message.chat.id]
       #team_name=user.team
       #if team_name == "Максим":
       db_worker.add_team(username, team)
       db_worker.close()

def read_team(username):
       db_worker = SQLighter(config.database_name)
       return db_worker.read_team_sql(username)
       db_worker.close()

    
                        
def player_exists (name):
       #chat_id = message.chat.id
       #chat_id = message
       db_worker = SQLighter(config.database_name)
      # user = user_dict[message.chat.id]
       #team_name=user.team
       #if team_name == "Максим":
       return db_worker.player_exists(name)
       
       db_worker.close()


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, """Проверьте список необходимых предметов для игры: 
- Автомобиль 
- 3-5 друзей 
- Навигатор с картой Тулы 
- Доступ в интернет с мобильного 
- Блокнот 
- Ручка 
- Телефон с фотокамерой 
- Установленное приложение Telegram 
- Зеркало

Во время игры, вы будете сталкиваться с различного рода игровой атрибутикой и различного рода девайсами – убедительная просьба НЕ портить игровое имущество.""")
    

    
# Handle '/start' and '/help'
@bot.message_handler(commands=['startgame'])
def send_welcome(message):
    chat_id = message.chat.id
   # bot.send_message(chat_id, message.from_user.username)
    #global gamestarted
    #gamestarted=0
    global hintcount
    hintcount =0
    global codeindex
    codeindex = 0
    global currentquestion
    currentquestion = 0
    global starttime
    global questsum
    questsum=0
    starttime=message.date
    username=message.from_user.username
    #bot.send_message(chat_id, str(player_exists(username)))
    if str(player_exists(username))=="[(0,)]":
        #bot.send_message(chat_id, str(player_exists(username)))
        create_new_player(chat_id, username, starttime)
        msg = bot.send_message(chat_id, """\
Добрый день!
Как тебя зовут?
""")
        bot.register_next_step_handler(msg, process_team_step)
    else:        
       # bot.send_message(chat_id, str(player_exists(username)))
        msg = bot.send_message(chat_id,"Привет, "+message.from_user.first_name+"! Давно не виделись! Напиши, как тебя зовут сегодня?")
        bot.register_next_step_handler(msg, process_team_step)
    

def process_team_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Кирилл', 'Максим')
        msg = bot.send_message(chat_id, 'В чьей ты команде?', reply_markup=markup)
        #msg = bot.send_message(chat_id, config.database_name)
        bot.register_next_step_handler(msg, process_choose_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_choose_step(message):
    try:
        chat_id = message.chat.id
        team = message.text
        username=message.from_user.username
        #bot.send_message(chat_id, username)
        user = user_dict[chat_id]
        if (team == u'Кирилл') or (team == u'Максим'):
            user.team = team
            add_team(username, user.team)
           # bot.send_message(chat_id, user.team)
        else:
            raise Exception()
        bot.send_message(chat_id, 'Удачной игры, ' + user.name + '\nТы в команде: ' + user.team)        
        bot.send_message(chat_id, "Задание 1.1.  Добрейшего денечка уважаемые игроки! Вы попали на шоу Угадай мелодию! И первый же вопрос Вам задаст Валдис Пельш!")     
        send_picture(message, 'valdis')  
        bot.send_message(chat_id, "Введите название этой песни?")  
        send_music(message, 'song#1')
        bot.send_message(chat_id, "Формат ответа: песни, слитно, без пробелов, с маленькой буквы.")
        #global gamestarted
        #getstarted==1
        bot.send_message(chat_id, gamestarted)
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
    bot.send_message(msg.chat.id, str(questions[code])) 

#@bot.message_handler(commands=['код'])
@bot.message_handler(func=lambda message: message.text)
def game(message):
    global currentquestion
    global codeindex
    global hintcount
    global questsumt
    global getstarted
    chat_id = message.chat.id
    #user = user_dict[chat_id]
    if message.text in codes:
        codeindex=codes.index(message.text)
        try:
            if codeindex == 0:
                bot.send_message(message.chat.id, "Код принят!")
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
            #send_picture(message, 'photo')
                give_next_question(message, codeindex)
           # bot.send_message(message.chat.id, "пупок")
                questsum=questsum+18
                #bot.send_message(message.chat.id, questsum)
           #answerssum +=codeindex
            
    #    questionindex=questions.index(codeindex)
            elif codeindex == 1:
                bot.send_message(message.chat.id, "Код принят!")
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
            #send_music(message, 'song')
                give_next_question(message, codeindex)
                send_picture(message, 'cool-pike')
                questsum=questsum+10
                bot.send_message(message.chat.id, """ Примечание: загадано точное место. Вам потребуется фотокамера. Бумагу с данными на загаданном месте НЕ СРЫВАТЬ!
            
    Формат ответа: одно слово на русском.""")
                                     
            elif codeindex == 2:
                bot.send_message(message.chat.id, "Код принят!")
                give_next_question(message, codeindex)
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
                questsum=questsum+12

            
            elif codeindex == 3:
                bot.send_message(message.chat.id, "Код принят!")
                give_next_question(message, codeindex)
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
                questsum=questsum+12
            
            elif codeindex == 4:
                bot.send_message(message.chat.id, "Код принят!")
                give_next_question(message, codeindex)
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
                questsum=questsum+12
            
            elif codeindex == 5:
                bot.send_message(message.chat.id, "Код принят!")
                give_next_question(message, codeindex)
                send_picture(message, 'pru')
                send_picture(message, 'piper')
                send_picture(message, 'fibi')
                bot.send_message(message.chat.id, """
Скорее осмотрите эти места! Возможно сестры оставили для вас там подсказки!

Примечание: Задание составное из трех частей. Всего загаданных мест три. Вам нужно собрать составной код и вбить его в правильном порядке целиком без пробелов в движок.""")
                
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
                questsum=questsum+12
            
            elif codeindex == 6:
                bot.send_message(message.chat.id, "Код принят!")
                give_next_question(message, codeindex)
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
                questsum=questsum+12
            
            elif codeindex == 7:
                bot.send_message(message.chat.id, "Код принят!")
                give_next_question(message, codeindex)
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
                questsum=questsum+12
            
            elif codeindex == 8:
                hintcount=0
                currentquestion +=1                
                bot.send_message(message.chat.id, "Код принят!")
                save_code_to_base(chat_id, message.from_user.username, str(codes[codeindex]))
            #answerssum +=codeindex
                endtime=message.date-starttime
                global getstarted
                getstarted==0
                bot.send_message(message.chat.id, "Конец игры! Ваше время "+time.strftime('%H:%M:%S', time.gmtime(endtime)))         
            else:
                bot.send_message(message.chat.id, "Код неверный!")
        except:
            bot.send_message(message.chat.id, "Что-то пошло не так!")
    elif message.text not in codes:    
        bot.send_message(message.chat.id, "Неверный код!")
    
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
