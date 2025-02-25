"""
BeautifulSoup code from https://www.geeksforgeeks.org/how-to-scrape-websites-with-beautifulsoup-and-python/
"""

import requests
import json
from bs4 import BeautifulSoup

# Create a dictionary to store the final information in, then make a GET request to parse the website's HTML through BeautifulSoup
menu_json = {}
menu_request = requests.get("https://www.mcdonalds.com/us/en-us/full-menu.html")
menu_soup = BeautifulSoup(menu_request.content, "html.parser")

# Gets all menu items avaliable on the webpage. In the HTML code, all menu items have the class "cmp-category__item"
all_items = menu_soup.find_all(class_="cmp-category__item")
total_items = 0

# Use McDonalds' API to fetch data about a menu item when given its id.
def get_item_info(id: int) -> any:
    page = f"https://www.mcdonalds.com/dnaapp/itemDetails?country=US&language=en&showLiveData=true&item={id}"
    request = requests.get(page).content
    info = json.loads(request) # Parse the request with the json module so the data can be read as a dictionary
    category = info["item"]["default_category"]["category"]["name"]
    name = info["item"]["item_name"]
    nutrition = {
        "calories" : int(info["item"]["nutrient_facts"]["nutrient"][0]["value"]),
        "protien" : int(info["item"]["nutrient_facts"]["nutrient"][0]["value"]),
        
    }
    return (category, name, nutrition)

for item in all_items:
    if item.find_parent(id="maincatcontent"): # Ignores items in the "Featured Favorites" category as they are already in the normal menu
        continue
    else:
        total_items += 1
        item_id = item["data-product-id"] # Get the id of an item by finding its HTML attributes
        item_info = get_item_info(item_id)
        print(item_info)
        break