"""
BeautifulSoup resources from https://www.geeksforgeeks.org/how-to-scrape-websites-with-beautifulsoup-and-python/
I should of made this with async
"""
import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path

# Make a GET request to parse the website's HTML through BeautifulSoup
menu_request = requests.get("https://www.mcdonalds.com/us/en-us/full-menu.html")
menu_soup = BeautifulSoup(menu_request.content, "html.parser")

# Gets all menu items available on the webpage. In the HTML code, all menu items have the class "cmp-category__item"
all_items = menu_soup.find_all(class_="cmp-category__item")

# Tuple to prevent properties that aren't needed from getting added to item information (for the sake of the program)
blacklisted_info = ("energy_kJ", "fibre2015", "calories_from_fat") 

# Use McDonalds' API to fetch data about a menu item when given its id.
def get_item_info(id: int) -> tuple[str, str, dict] | str:
    page = f"https://www.mcdonalds.com/dnaapp/itemDetails?country=US&language=en&showLiveData=true&item={id}"
    request = requests.get(page).content
    info = json.loads(request) # Parse the request with the json module so the data can be read as a dictionary
    name = info["item"]["item_name"]
    category = ""
    nutrition = {}
    try:
        if "category" in info["item"]["default_category"]: # Compensate for items with no category or the script will crash
            category = info["item"]["default_category"]["category"]["name"]
        else:
            category = "Miscellaneous"

        if info["item"]["item_type"] == "Item Collection": # Reassign the request to a different API call that combo items use
            page = f"https://www.mcdonalds.com/dnaapp/itemCollectionDetails?country=US&language=en&showLiveData=true&item={id}" 
            request = requests.get(page).content
            info = json.loads(request)
            # FOR SOME REASON mcdonald's app does not have the meal_item table for the 4 Piece McChicken Nugget Happy Meal, so it will not work.
            for nutrient in info["meal_item"]["collective_nutrition"]["nutrient_facts"]["nutrient"]:
                nutrient_key = nutrient["nutrient_name_id"]
                if nutrient_key in blacklisted_info:
                    continue
                nutrient_value, nutrient_uom = float(nutrient["value"]), nutrient["uom"]
                nutrition[nutrient_key] = (nutrient_value, nutrient_uom)
        else:
            for nutrient in info["item"]["nutrient_facts"]["nutrient"]:
                nutrient_key = nutrient["nutrient_name_id"]
                if nutrient_key in blacklisted_info:
                    continue
                nutrient_value, nutrient_uom = float(nutrient["value"]), nutrient["uom"]
                nutrition[nutrient_key] = (nutrient_value, nutrient_uom)
        return (category, name, nutrition)
    except Exception as err:
        return f"FAILURE AT {id}: {name}. Cause: {err}"

def create_item_list(output_file: any) -> str:
    total_items = 0
    # Missing items used for debugging and clarity
    missing_items = 0
    menu_json = {}
    for item in all_items:
        if item.find_parent(id="maincatcontent"): # Ignores items in the "Featured Favorites" category as they are already in the normal menu
            continue
        else:
            item_id = item["data-product-id"] # Get the id of an item by finding its HTML attributes
            item_info = get_item_info(item_id)
            if type(item_info) == tuple:
                if not (item_info[0]) in menu_json: # Creates categories if they are not found in the list already
                    print(f"New Category: {item_info[0]}")
                    menu_json[item_info[0]] = {}

                menu_json[item_info[0]][item_id] = {"name" : item_info[1], "nutrition_info" : item_info[2]}
                print(item_info[1])
                total_items += 1
            else:
                missing_items += 1
                print(item_info)
                input("Press enter to unpause script")

    menu_json["total_items"] = total_items
    menu_json["missing_items"] = missing_items
    json.dump(menu_json, output_file, indent=2) # Resource used: https://www.geeksforgeeks.org/json-dump-in-python/ Indent is used to make the file visually appealing
    return "Success"
relative_path = Path(__file__).parent # Resource used: https://stackoverflow.com/a/51149057

with open(f"{relative_path}/mcdonaldmenu_output.json", "w") as file: # Opening a file in write mode will create it if it doesn't exist prior to the function's call
    result = create_item_list(file)
    print(result)
