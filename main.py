"""
Creating chatbot via Telegram API
"""
import telebot
from token_data import Token
from data_loader import DataLoader
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message


token = Token().get_token()

class Club:
    def __init__(self, name, info):
        self.name = name
        self.info = info

    def get_info(self):
        return f"{self.name} \n\n{self.info[1]}\n \n \n Подробнее о клубе можешь узнать здесь: \n{self.info[0]}"


class Subject:
    def __init__(self, name, clubs):
        self.name = name
        self.clubs = clubs

    def get_club_buttons(self):
        markup = InlineKeyboardMarkup()
        row = [] 
        for club in self.clubs:
            row.append(InlineKeyboardButton(club.name, callback_data=f'club_{club.name}'))

            if len(row) == 2:
                markup.add(*row)
                row = []
        if row:
            markup.add(*row)

        return markup


class ClubBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token, parse_mode=None)
        self.subjects = []
        self.load_data()
        self.setup_handlers()
        self.delete_webhook()

    def delete_webhook(self):
        self.bot.delete_webhook()

    def load_data(self):
        data_loader = DataLoader('clear_data.json', 'questions.json')
        data, self.additional_questions = data_loader.load_data()
        
        for subject_name, clubs_info in data.items():
            clubs = [Club(name, info) for name, info in clubs_info.items()]
            self.subjects.append(Subject(subject_name, clubs))

    def setup_handlers(self):
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query_handler(call: CallbackQuery):
            if call.data == "yes":
                self.ask_about_subject(call.message)
            elif call.data == "no":
                self.bot.send_message(call.message.chat.id, "Мне жаль, что тебе не интересна "
                                                            "внеучебная деятельность. \n\nНо если "
                                                            "ты всё же передумаешь и захочешь "
                                                            "начать снова, нажми на /start \n\n"
                                                            "Надеюсь, что буду полезным в будущем :)")
            elif call.data.isdigit():
                subject_index = int(call.data)
                subject = self.subjects[subject_index]
                club_buttons = subject.get_club_buttons()
                self.bot.send_message(call.message.chat.id, f"{subject.name} - отличный выбор! \n"
                                                            "Ты можешь узнать подробную информацию о клубах, "
                                                            "нажав на одну из кнопок ниже:", 
                                    reply_markup=club_buttons)
            elif call.data.startswith('club_'):
                club_name = call.data.replace('club_', '')
                club_info = next(club.get_info() for subject in self.subjects for club in subject.clubs if club.name == club_name)
                self.bot.send_message(call.message.chat.id, club_info)
            elif call.data == 'additional_info':
                self.bot.send_message(call.message.chat.id, self.additional_questions, parse_mode='HTML')
        
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message: Message):
            text = '''Привет, меня зовут КЛУБень!
Я бот студентов ФиПЛа, который поможет тебе разобраться во внеучебной деятельности Нижнегородской Вышки.

Здесь ты можешь найти информацию по действующим клубам, контактные данные для создания собственного клуба и многое другое.

Давай расскажу!'''
            self.bot.reply_to(message, text)
            self.ask_about_add_activities(message)

    def ask_about_add_activities(self, message: Message) -> None:
        text = "Хотел бы ты больше узнать о внеучебных клубах Нижегородской вышки?"
        markup = InlineKeyboardMarkup(row_width=2)
        yes_button = InlineKeyboardButton("Да!", callback_data="yes")
        no_button = InlineKeyboardButton("Нет(", callback_data="no")
        markup.add(yes_button, no_button)
        self.bot.send_message(message.chat.id, text, reply_markup=markup)

    def ask_about_subject(self, message: Message) -> None:
        text = "В Нижегородской вышке есть следующие направления внеучебной деятельности:"
        markup = InlineKeyboardMarkup()
        for index, subject in enumerate(self.subjects):
            markup.add(InlineKeyboardButton(subject.name, callback_data=str(index)))

        self.bot.send_message(message.chat.id, text, reply_markup=markup)

    def start_polling(self):
        self.bot.polling()


if __name__ == "__main__":
    club_bot = ClubBot(token)
    club_bot.start_polling()