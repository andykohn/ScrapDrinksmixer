from lxml import html
import requests
import re
import datetime
import json
import time

INGREDIENT_BASE = 1000
DRINK_BASE = 20000
ingredients_list = list()


def get_pages():

    pages = list()

    pages.append('http://www.drinksmixer.com/drink10001.html')
    pages.append('http://www.drinksmixer.com/drinkuv15392.html')
    return pages


def get_ingredients(tree):
    ingredients = list()
    elements_found = True
    i = 0
    while elements_found:
        i += 1
        element = tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/span[' + str(i) + ']/span[2]/a/text()')

        if element:
            ingredient_amount = re.sub('[^A-Za-z0-9\.]+', ' ',
                                       (tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/span['
                                                   + str(i) + ']/span[1]/text()'))[0]
                                       )
            ingredient = re.sub('[^A-Za-z0-9\.]+', ' ',
                                (tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/span['
                                            + str(i) + ']/span[2]/a/text()'))[0]
                                )

            if ingredient not in ingredients_list:
                ingredients_list.append(ingredient)

            ingredient_id = INGREDIENT_BASE + ingredients_list.index(ingredient)

            ingredients.append((i, ingredient_id, ingredient_amount))

        else:
            elements_found = False

    return ingredients


def process_pages(pages):
    drinks_list = list()

    for page in pages:
        # webpage = requests.get('http://www.drinksmixer.com/drink10001.html')
        webpage = requests.get(page)
        tree = html.fromstring(webpage.content)

        drink_name = re.sub('[^A-Za-z0-9\.]+', ' ',
                            (tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/span/h1/text()'))[0]
                            )

        drink_instructions = re.sub('[^A-Za-z0-9\.]+', ' ',
                                    (tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[3]/text()'))[0]
                                    )
        ingredients = get_ingredients(tree)
        drinks_list.append((drink_name, drink_instructions, ingredients))

        time.sleep(1)

    return drinks_list


def write_drinks_to_file(drinks):

    f = open('output/drinksmixer_drinks.json', 'w')
    for index, drink in enumerate(drinks):
        drink_json = dict()
        drink_json['idDrink'] = DRINK_BASE + index
        drink_json['strDrink'] = drink[0]
        drink_json['strCategory'] = 'Cocktail'
        drink_json['strAlcoholic'] = 'Alcoholic'
        drink_json['strGlass'] = None
        drink_json['strInstructions'] = drink[1]
        drink_json['strDrinkThumb'] = None
        drink_json['dateModified'] = str(datetime.date.today())

        json_data = json.dumps(drink_json)
        f.write(json_data + '\n')


def write_ingredients_to_file(ingredients_list):

    f = open('output/drinksmixer_ingredients.json', 'w')
    for ingredient in ingredients_list:
        drink_json = dict()
        drink_json['ingredientId'] = INGREDIENT_BASE + ingredients_list.index(ingredient)
        drink_json['name'] = ingredient

        json_data = json.dumps(drink_json)
        f.write(json_data + '\n')


def write_map_ingredient_drink_to_file(drinks, ingredients_list):

    f = open('output/drinksmixer_drinks.json', 'w')
    for index, drink in enumerate(drinks):

        map_ingredient_drink_json = dict()
        map_ingredient_drink_json['drinkId'] = DRINK_BASE + index
        map_ingredient_drink_json['ingredientId'] = ingredient
        map_ingredient_drink_json['measurement'] = ingredient
        map_ingredient_drink_json['iorder'] = ingredient

        json_data = json.dumps(map_ingredient_drink_json)
        f.write(json_data + '\n')

drinks_list = process_pages(get_pages())

write_drinks_to_file(drinks_list)
write_ingredients_to_file(ingredients_list)
write_map_ingredient_drink_to_file(drinks_list, ingredients_list)

# print drinks

#for ing in ingredients_list:
#    print INGREDIENT_BASE + ingredients_list.index(ing), ing
# print drink_name
#print drink_instructions
#print ingredients
# print datetime.date.today()

# drink_json = dict()
# drink_json['idDrink'] = '1'
# drink_json['strDrink'] = drink_name
# drink_json['strCategory'] = 'Cocktail'
# drink_json['strAlcoholic'] = 'Alcoholic'
# drink_json['strGlass'] = None
# drink_json['strInstructions'] = drink_instructions
# drink_json['strDrinkThumb'] = None
# drink_json['dateModified'] = str(datetime.date.today())

# f = open('output/drinksmixer_drinks.json', 'w')
# json_data = json.dumps(drink_json)
# f.write(json_data)

# f = open('output/drinksmixer_ingredients.json', 'w')
# json_data = json.dumps(drink_json)
# f.write(json_data)


# print json_data
