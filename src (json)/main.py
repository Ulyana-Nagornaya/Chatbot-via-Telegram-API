"""
Creating chatbot via Telegram API
"""
import telebot
from data_loader import DataLoader
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from token_data import Token


class Club:
    """
    Club class
    """
    def __init__(self, name: str, info: str) -> None:
        """
        Bot initialization

        Args:
            name (str): name
            info (str): info
        """
        self.name = name
        self.info = info

    def get_info(self) -> str:
        """
        Get info about club
        """
        return f"{self.name} \n\n{self.info[1]}\n \n \n " \
               f"Подробнее о клубе можешь узнать здесь: \n{self.info[0]}"


class Subject:
    """
    Club subject class
    """
    def __init__(self, name: str, clubs: list) -> None:
        """
        Bot initialization

        Args:
            name (str): name
            clubs (list): club list
        """
        self.name = name
        self.clubs = clubs

    def get_club_buttons(self) -> InlineKeyboardMarkup:
        """
        Get club buttons
        """
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
    """
    Bot class
    """
    def __init__(self, token: str) -> None:
        """
        Bot initialization

        Args:
            token (str): token string
        """
        self.bot = telebot.TeleBot(token, parse_mode=None)
        self.subjects = []
        self.last_msg = 'Надеюсь, что смог помочь тебе и информация была полезной! \n' \
                        'А если тебя ничего не заинтересовало, может, ты хочешь создать' \
                        ' свой собственный клуб? В таком случае можно обратиться к ' \
                        '**Шмелёву Степану Викторовичу** - главе внеучебной деятельности ' \
                        'НИУ ВШЭ \n https://vk.com/id307399746 \n\nДо новых встреч :) \n' \
                        '\n Если захочешь снова начать со мной общение, нажми на /start'
        self.load_data()
        self.setup_handlers()
        self.additional_question = {}

    def load_data(self) -> None:
        data_loader = DataLoader('dataset/clear_data.json', 'dataset/questions.json')
        data, self.additional_questions = data_loader.load_data()

        for subject_name, clubs_info in data.items():
            clubs = [Club(name, info) for name, info in clubs_info.items()]
            self.subjects.append(Subject(subject_name, clubs))

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
                self.ask_about_subject(call.message)
            elif call.data == "no":
                self.bot.send_message(call.message.chat.id,
                                      "Мне жаль, что тебе не интересна "
                                        "внеучебная деятельность. \n\nНо если "
                                        "ты всё же передумаешь и захочешь "
                                        "начать снова, нажми на /start \n\n"
                                        "Надеюсь, что буду полезным в будущем :)")
            elif call.data.isdigit():
                subject_index = int(call.data)
                subject = self.subjects[subject_index]
                club_buttons = subject.get_club_buttons()
                self.bot.send_message(call.message.chat.id,
                                      f"{subject.name} - отличный выбор! \n"
                                        "Ты можешь узнать подробную информацию о клубах, "
                                        "нажав на одну из кнопок ниже:",
                                      reply_markup=club_buttons)
            elif call.data.startswith('club_'):
                club_name = call.data.replace('club_', '')
                club_info = next(club.get_info() for subject in self.subjects
                                 for club in subject.clubs if club.name == club_name)
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
        def handle_text(message):
            text_markup = 'Извини, не могу ответить на твое сообщение\nВозможно, ты найдешь интересующую информацию ниже по кнопке?'
            add_text_markup = telebot.types.InlineKeyboardMarkup()
            text_message = telebot.types.InlineKeyboardButton("Дополнительная информация", callback_data="additional_info")
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

    def ask_about_subject(self, message: Message) -> None:
        """
        Ask about subject

        Args:
            message (Message): message of bot
        """
        text = "В Нижегородской вышке есть следующие направления внеучебной деятельности:"
        markup = InlineKeyboardMarkup()
        for index, subject in enumerate(self.subjects):
            markup.add(InlineKeyboardButton(subject.name, callback_data=str(index)))

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

    def start_polling(self) -> None:
        """
        Polling
        """
        self.bot.polling()


# if __name__ == "__main__":
#     token = Token().get_token()

#     club_bot = ClubBot(token)
#     club_bot.start_polling()