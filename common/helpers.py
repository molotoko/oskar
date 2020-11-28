import random
import requests
import lxml.html as html

from .vars import members_list


def random_member():
    random_member_choice = random.choice(members_list)

    return random_member_choice['username']


def get_random_actor(gender):
    link_old = 'https://www.imdb.com/search/name/?groups=oscar_winner,oscar_nominee&count=100'
    link = 'https://www.imdb.com/search/name/?count=100'
    start = random.randint(1, 500)

    if gender:
        link = f'{link}&gender={gender}&start={start}'

    actors_request = requests.get(link)
    actors_tree = html.fromstring(actors_request.text)
    actors = actors_tree.find_class('lister-item')

    actor = random.choice(actors).find_class('lister-item-header')[0].find('a')
    actor_name = actor.text_content().strip()
    actor_href = actor.attrib['href']
    actor_link = f'https://www.imdb.com{actor_href}'

    actor_request = requests.get(actor_link)
    actor_tree = html.fromstring(actor_request.text)
    actor_death_info = actor_tree.xpath('//div[@id="name-death-info"]')

    return {
        'name': actor_name,
        'link': actor_link,
        'alive': False if len(actor_death_info) else True
    }


def get_random_director():
    # get 250 best directors list from IMDB
    page_number = random.choice([1, 2, 3])
    link = f'https://www.imdb.com/list/ls008344500/?sort=list_order,asc&mode=detail&page={page_number}'

    directors_request = requests.get(link)
    directors_tree = html.fromstring(directors_request.text)
    directors = directors_tree.find_class('lister-item')

    director = random.choice(directors).find_class('lister-item-header')[0].find('a')
    director_name = director.text_content().strip()
    director_href = director.attrib['href']
    director_link = f'https://www.imdb.com{director_href}'

    return {
        'name': director_name,
        'link': director_link
    }


def born_today():
    request_link = 'https://www.imdb.com/feature/bornondate/'
    page = requests.get(request_link)
    tree = html.fromstring(page.text)

    born_list = []
    celebrities = tree.find_class('lister-item')[:5]

    for celebrity in celebrities:
        celebrity_anchor = celebrity.find_class('lister-item-header')[0].find('a')
        celebrity_name = celebrity_anchor.text_content().strip()
        celebrity_link = celebrity_anchor.attrib['href']
        born_list.append([celebrity_name, celebrity_link])

    born_message = f'Сегодня родились знаменитости:\n'
    for celebrity in born_list:
        born_message += f'[{celebrity[0]}](https://www.imdb.com{celebrity[1]})\n'

    return born_message

# @bot.message_handler(content_types=['sticker'])
# def send_sticker_id(message):
#     bot.send_message(message.chat.id, message.sticker.file_id)
