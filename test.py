from lxml import html
import requests
import re
import datetime
import json
import time

webpage = requests.get("http://www.drinksmixer.com/drink8428.html")
tree = html.fromstring(webpage.content)


drinks = tree.xpath("//div[contains(@class, 'RecipeDirections instructions')]/text()")

print drinks
