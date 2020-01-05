import random
import telebot
import requests
import lxml.html as html
import unicodedata
from config import telegram_api_key

bot = telebot.TeleBot(telegram_api_key)
members_list = [
        'Лиза', 'Дроид', 'МикМал', 'Маду', 'Фывдло', 'Олень', 'Ира', 'Анечка', 'Кэт', 'Милли', 'Гедарк', 'Марта',
        'Цунали', 'Кокос'
    ]


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Приветствую тебя, о киноман!')


@bot.message_handler(commands=['help'])
def get_vip(message):
    bot.send_message(
        message.chat.id,
        f'Добро пожаловать к Оскару в Киноклуб! Ниже представлен список моих услуг. Помните: судьба может сыграть с вами'
        f' злую шутку!\n'
        f'/member расскажет обо всех ваших кинотайнах;\n'
        f'/film выберет за вас случайное кино;\n'
        f'/genre поможет выбрать жанр для голосований (если повезет — с эротикой);\n'
        f'/vip определит особо голосистого участника этого голосования;\n'
        f'/kinoman даст одному из вас возможность сразу предложить фильм вне очереди.',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['member'])
def member_info(message):
    get_info = 'собрать инфу из таблички'
    find_member_info = 'вытащить инфу о конкретном члене клуба'
    bot.send_message(message.chat.id, f'Ваша статистика пока недоступна.')


@bot.message_handler(commands=['film'])
def random_film(message):
    page = requests.get('https://www.kinopoisk.ru/afisha/new/city/1/')
    tree = html.fromstring(page.text)
    film_name = tree.xpath('//div[@class="randomMovie"]//a/span/u/text()')[0]
    film_name_normalized = unicodedata.normalize("NFKD", film_name)
    film_path = 'film/301/'

    all_links = list(tree.iterlinks())
    for link in all_links:
        (element, attribute, url, pos) = link
        if 'level/1/film' in url:
            film_path = url[8:]
    film_link = f'https://www.kinopoisk.ru{film_path}'

    bot.send_message(
        message.chat.id,
        f'Вам придется посмотреть фильм "{film_name_normalized}": {film_link}',
        reply_to_message_id=message.message_id
    )


@bot.message_handler(commands=['genre'])
def random_genre(message):
    genre_list = ['аниме', 'биография', 'боевик', 'вестерн', 'военный', 'детектив', 'документальный', 'драма',
                  'история', 'комедия', 'короткометражка', 'криминал', 'мелодрама', 'музыка', 'мультфильм',
                  'приключения', 'семейный', 'спорт', 'триллер', 'ужасы', 'фантастика', 'фильм-нуар', 'фэнтези']
    genre_value = random.choice(genre_list)

    erotic = ' с эротикой'
    if random.randrange(0, 100) < 2:
        genre_value = f'{genre_value}{erotic}'

    bot.send_message(
        message.chat.id,
        f'*Выбран жанр*: {genre_value}.',
        parse_mode='Markdown',
        reply_to_message_id=message.message_id
    )


@bot.message_handler(commands=['vip'])
def get_vip(message):
    random_member = random.choice(members_list)

    bot.send_message(
        message.chat.id,
        f'Киноман *{random_member}* получил статус *VIP*. Это значит, что он имеет 4 голоса вместо 2 и может '
        f'распределить их как угодно, но не более 2 голосов за 1 фильм.',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['kinoman'])
def kinoman_of_the_week(message):
    random_member = random.choice(members_list)

    bot.send_message(
        message.chat.id,
        f'Киноман *{random_member}* становится почетным *Киноманом Недели*. '
        f'Он может предложить любой фильм к просмотру вне очереди!',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['santa'])
def santa(message):
    random_member = random.choice(members_list)

    bot.send_message(
        message.chat.id,
        f'Киноман *{random_member}* становится Сантой. '
        f'Он может предложить любой фильм к просмотру вне очереди!\n'
        f'Этот фильм мы занесем в Коллективные просмотры!',
        parse_mode='Markdown'
    )


@bot.message_handler(content_types=['text'])
def send_text(message):
    hello_list = ['привет', 'hello', 'hi', 'приветствую', 'здравствуй', 'здравствуйте', 'хелло', 'хэлло', 'йоу',
                  'здрасьте', 'дратути', 'драсьте']
    if message.text.lower() in hello_list:
        bot.send_message(message.chat.id, 'Привет, киноман!')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'I\'ll be back!')


bot.polling()
