"""
Creating chatbot via Telegram API.
"""
import os
from pathlib import Path

import telebot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.clubs_database import Category, Database
from src.data_loader import DataLoader
from src.token_data import TOKEN


class ClubBot:
    """
    Bot class
    """
    def __init__(self, bot_token: str,
                 database: Database,
                 questions_path: Path | str = '') -> None:
        """
        Bot initialization.

        Args:
            bot_token (str): Token string
            database_password (str): Password
        """
        self.bot = telebot.TeleBot(bot_token, parse_mode=None)
        self.categories = []
        self.last_msg = 'Надеюсь, что смог помочь тебе и информация была полезной! \n' \
                        'А если тебя ничего не заинтересовало, может, ты хочешь создать' \
                        ' свой собственный клуб? В таком случае можно обратиться к ' \
                        '**Шмелёву Степану Викторовичу** - главе внеучебной деятельности ' \
                        'НИУ ВШЭ \n https://vk.com/id307399746 \n\nДо новых встреч :) \n' \
                        '\n Если захочешь снова начать со мной общение, нажми на /start'
        self.database = database
        self.categories = self.database.load_data()

        self.dataloader = DataLoader(questions_path)
        self.additional_questions = ''
        if self.dataloader.questions_path:
            self.dataloader.load_questions()
            self.additional_questions = self.dataloader.additional_questions

        self.setup_handlers()

    def setup_handlers(self) -> None:
        """
        Set up handlers
        """
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query_handler(call: CallbackQuery) -> None:
            """
            Handle callback query

            Args:
                call (CallbackQuery): callback query
            """
            if call.data == "yes":
                self.ask_about_category(call.message)
            elif call.data == "no":
                self.bot.send_message(call.message.chat.id,
                                      "Мне жаль, что тебе не интересна "
                                        "внеучебная деятельность. \n\nНо если "
                                        "ты всё же передумаешь и захочешь "
                                        "начать снова, нажми на /start \n\n"
                                        "Надеюсь, что буду полезным в будущем :)")
            elif call.data.isdigit():
                category_index = int(call.data)
                category = self.categories[category_index]
                club_buttons = self.buttons_for_category(category)
                self.bot.send_message(call.message.chat.id,
                                      f"{category.name} - отличный выбор! \n"
                                        "Ты можешь узнать подробную информацию о клубах, "
                                        "нажав на одну из кнопок ниже:",
                                      reply_markup=club_buttons)
            elif call.data.startswith('club_'):
                club_name = call.data.replace('club_', '')
                club_info = next(club.get_info() for category in self.categories
                                 for club in category.clubs if club.name == club_name)
                self.bot.send_message(call.message.chat.id, club_info)
            elif call.data == 'additional_info':
                self.bot.send_message(call.message.chat.id,
                                      self.additional_questions,
                                      parse_mode='HTML')
            elif call.data == 'None':
                self.bot.send_message(call.message.chat.id,
                                      self.last_msg, parse_mode='Markdown')

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message: Message) -> None:
            """
            Send welcome message

            Args:
                message (Message): message of bot
            """
            text = 'Привет, меня зовут КЛУБень!\n'\
                    'Я бот студентов ФиПЛа, который поможет'\
                    'тебе разобраться во внеучебной деятельности ' \
                    'Нижегородской Вышки.\n\n' \
                    'Здесь ты можешь найти информацию по действующим' \
                    ' клубам, контактные данные для создания' \
                    ' собственного клуба и многое другое.\n\n' \
                    'Давай расскажу!\n\n' \
                    'Инструкцию по использованию ты можешь найти по команде /help'
            self.bot.reply_to(message, text)
            self.ask_about_add_activities(message)

        @self.bot.message_handler(commands=['help'])
        def send_help(message: Message) -> None:
            """
            Send help message

            Args:
                message (Message): message of bot
            """
            text = 'Если ты не можешь разобраться в том, как работает бот, ' \
                   'вот ссылка на инструкцию по использованию: \n' \
                   'https://github.com/AnPruch/tuberous_club'
            self.bot.reply_to(message, text)

        @self.bot.message_handler(content_types=['text'])
        def handle_text(message: Message) -> None:
            text_markup = 'Извини, не могу ответить на твое сообщение\n' \
                          'Возможно, ты найдешь интересующую информацию ниже по кнопке?'
            add_text_markup = telebot.types.InlineKeyboardMarkup()
            text_message = telebot.types.InlineKeyboardButton("Дополнительная информация",
                                                              callback_data="additional_info")
            add_text_markup.add(text_message)
            self.bot.send_message(message.chat.id, text_markup, reply_markup=add_text_markup)

    def ask_about_add_activities(self, message: Message) -> None:
        """
        Ask about start

        Args:
            message (Message): message of bot
        """
        text = "Хотел бы ты больше узнать о внеучебных клубах Нижегородской вышки?"
        markup = InlineKeyboardMarkup(row_width=2)
        yes_button = InlineKeyboardButton("Да!", callback_data="yes")
        no_button = InlineKeyboardButton("Нет(", callback_data="no")
        markup.add(yes_button, no_button)
        self.bot.send_message(message.chat.id, text, reply_markup=markup)

    def ask_about_category(self, message: Message) -> None:
        """
        Ask about category

        Args:
            message (Message): message of bot
        """
        text = "В Нижегородской вышке есть следующие направления внеучебной деятельности:"
        markup = InlineKeyboardMarkup()
        for index, category in enumerate(self.categories):
            markup.add(InlineKeyboardButton(category.name, callback_data=str(index)))

        self.bot.send_message(message.chat.id, text, reply_markup=markup)
        sent_msg = "Ну как? Есть что-то интересное именно для тебя? " \
                   "Нажми на кнопку выше и выбери направление, чтобы узнать, " \
                   "какие клубы туда входят"
        self.bot.send_message(message.chat.id, sent_msg)
        self.ask_about_additional_info(message)

    def ask_about_additional_info(self, message: Message) -> None:
        """
        Ask about additional info

        Args:
            message (Message): message of bot
        """
        additional_message = "Если тебя ничего не заинтересовало, " \
                             "или ты хочешь узнать дополнительную информацию, " \
                             "нажми на кнопку ниже"
        additional_markup = InlineKeyboardMarkup()
        additional_info_button = InlineKeyboardButton("Дополнительная информация",
                                                      callback_data="additional_info")
        nothing_interested_button = InlineKeyboardButton("Ничего не заинтересовало",
                                                         callback_data='None')
        additional_markup.add(additional_info_button, nothing_interested_button)
        self.bot.send_message(message.chat.id, additional_message,
                              reply_markup=additional_markup)

    @staticmethod
    def buttons_for_category(category: Category) -> InlineKeyboardMarkup:
        """
        Create buttons for category
        """
        markup = InlineKeyboardMarkup()
        row = []
        for club in category.clubs:
            row.append(InlineKeyboardButton(club.name, callback_data=f'club_{club.name}'))

            if len(row) == 2:
                markup.add(*row)
                row = []
        if row:
            markup.add(*row)

        return markup

    def start_polling(self) -> None:
        """
        Polling
        """
        self.bot.polling()


if __name__ == "__main__":
    if os.environ.get('ENV') == 'production':
        database = Database(db_name='railway', user='postgres', password='zKbGbHPNygmKJojOUWtFyzVEXjFZuVyl',
                                    host='autorack.proxy.rlwy.net', port='20181')
    else:
        database = Database(db_name='tuberous_club', user='postgres',
                                    password='12345678', host='localhost',
                                    port='5432')
    club_bot = ClubBot(TOKEN, database,
                       questions_path=Path(__file__).parent.parent
                                      / 'dataset' / 'questions.json')
    
    club_bot.start_polling()
