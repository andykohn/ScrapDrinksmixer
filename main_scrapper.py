from lxml import html
import requests
import re
import datetime
import json
import time

INGREDIENT_BASE = 1000
DRINK_BASE = 20000
REGEX_TO_KEEP = "[^A-Za-z0-9'/:.]+"


def get_pages():

    pages = list()

    get_single_category_page(pages, 1, "Cocktails", 125) #125
    #get_single_category_page(pages, 2, "Punches", 7)
    #get_single_category_page(pages, 3, "Shot", 28)
    #get_single_category_page(pages, 4, "Beer", 5)
    #get_single_category_page(pages, 7, "Coffee & tea", 5)


    return pages


def get_single_category_page(pages, category_id, category, num_of_pages):
    links = list()
    for x in range(1, num_of_pages):
        if x == 2:
            break
        webpage = requests.get("http://www.drinksmixer.com/cat/" + str(category_id) + "/" + str(x))
        print("Getting page: http://www.drinksmixer.com/cat/" + str(category_id) + "/" + str(x))
        tree = html.fromstring(webpage.content)

        links.extend(tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[3]//@href'))
        time.sleep(0.1)

    for link in links:
        pages.append(('http://www.drinksmixer.com' + link, category))


def get_ingredients(tree, all_ingredients):
    ingredients = list()
    elements_found = True
    i = 0
    while elements_found:
        i += 1
        element = tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/span[' +
                             str(i) + ']/span[2]/a/text()')

        if element:
            ingredient_amount = re.sub(REGEX_TO_KEEP, ' ',
                                       (tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/span['
                                                   + str(i) + ']/span[1]/text()'))[0]
                                       )
            ingredient = re.sub(REGEX_TO_KEEP, ' ',
                                (tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/span['
                                            + str(i) + ']/span[2]/a/text()'))[0]
                                )

            if ingredient not in all_ingredients:
                all_ingredients.append(ingredient)

            ingredient_id = INGREDIENT_BASE + all_ingredients.index(ingredient)

            ingredients.append((i, ingredient_id, ingredient_amount))

        else:
            elements_found = False

    return ingredients


def process_pages(pages, all_ingredients):
    drinks = list()

    for index, page in enumerate(pages):
        print("Processing: " + str(index) + "/" + str(len(pages)) + ", " + page[0])
        if index == 2:
            break
        # webpage = requests.get(page[0])
        webpage = ''
        while webpage == '':
            try:
                webpage = requests.get(page[0])
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(5)
                print("Was a nice sleep, now let me continue...")
                continue


        tree = html.fromstring(webpage.content)

        drink_name = re.sub(REGEX_TO_KEEP, ' ',
                            (tree.xpath('/html/body/div/div[1]/div[1]/div[1]/div[2]/span/h1/text()'))[0]
                            )

        # Join the instructions from a list to a string and then remove special characters
        drink_instructions = re.sub(REGEX_TO_KEEP, ' ', (
            '. '.join((tree.xpath("//div[contains(@class, 'RecipeDirections instructions')]/text()")))))
        drink_ingredients = get_ingredients(tree, all_ingredients)
        drinks.append((drink_name, drink_instructions, drink_ingredients, page[1]))

        time.sleep(0.1)

    return drinks


def write_drinks_to_file(drinks):

    f = open('output/drinksmixer_drinks.json', 'w', 1)
    for index, drink in enumerate(drinks):
        drink_json = dict()
        drink_json['idDrink'] = DRINK_BASE + index
        drink_json['strDrink'] = drink[0]
        drink_json['strCategory'] = drink[3]
        drink_json['strAlcoholic'] = 'Alcoholic'
        drink_json['strGlass'] = None
        drink_json['strInstructions'] = drink[1]
        drink_json['strDrinkThumb'] = None
        drink_json['dateModified'] = str(datetime.date.today())

        json_data = json.dumps(drink_json)
        f.write(json_data + '\n')


def write_ingredients_to_file(ingredients):

    f = open('output/drinksmixer_ingredients.json', 'w')
    for ingredient in ingredients:
        drink_json = dict()
        drink_json['ingredientId'] = INGREDIENT_BASE + ingredients.index(ingredient)
        drink_json['name'] = ingredient

        json_data = json.dumps(drink_json)
        f.write(json_data + '\n')


def write_map_ingredient_drink_to_file(drinks):

    f = open('output/drinksmixer_map_ingredient_drink.json', 'w')
    for index, drink in enumerate(drinks):
        for ingredient in drink[2]:
            map_ingredient_drink_json = dict()
            map_ingredient_drink_json['drinkId'] = DRINK_BASE + index
            map_ingredient_drink_json['ingredientId'] = ingredient[1]
            map_ingredient_drink_json['measurement'] = ingredient[2]
            map_ingredient_drink_json['iorder'] = ingredient[0]

            json_data = json.dumps(map_ingredient_drink_json)
            f.write(json_data + '\n')


ingredients_list = list()

drinks_list = process_pages(get_pages(), ingredients_list)

write_drinks_to_file(drinks_list)
#write_ingredients_to_file(ingredients_list)
#write_map_ingredient_drink_to_file(drinks_list)


