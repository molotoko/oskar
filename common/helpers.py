import random
import requests
import lxml.html as html

from vars import members_list


def random_member():
    random_member_choice = random.choice(members_list)

    return random_member_choice['username']


def get_random_actor(gender):
    link = 'https://www.imdb.com/search/name/?groups=oscar_winner,oscar_nominee&count=100'

    if gender:
        link = f'{link}&gender={gender}'

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
