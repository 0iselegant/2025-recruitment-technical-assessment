from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = []

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	recipeName = re.sub(r'(-|_)', ' ', recipeName) # replace underscores and hyphens with empty space
	recipeName = re.sub(r'[^(a-zA-Z| )]', '', recipeName) # remove all non-letter, non-whitespace characters
	recipeName = re.sub(r' +', ' ', recipeName) # remove extra whitespace
	recipeName = ' '.join([word.capitalize() for word in recipeName.split(' ')]) # capitalise
	if len(recipeName) == 0:
		return None
	return recipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.get_json()
	
	# check that type exists, and that it is either recipe or ingredient
	if data.get("type", "") != "recipe" and data.get("type", "") != "ingredient":
		return "invalid entry type", 400

	# check that entryName exists, and that it hasn't already been used in the cookbook
	if not("name" in data):
		return "no name", 400
	for entry in cookbook:	
		if entry["name"] == data["name"]:
			return "duplicate name", 400

	if data["type"] == "ingredient" and "cookTime" in data and len(data) == 3: # validate fields for ingredient
		# if cook time exists, check that it is greater than zero
		if data["cookTime"] < 0:
			return "negative cookTime", 400
	elif data["type"] == "recipe" and len(data.get("requiredItems", [])) > 0 and len(data) == 3: # validate fields for recipe
		names = [item["name"] for item in data["requiredItems"]]
		if len(set(names)) != len(names):
			return "duplicate name in required items", 400
	else:
		return "invalid fields", 400

	cookbook.append(data)
	return "", 200
		

	# TODO: implement me
# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	name = request.args.get("name", default=None)
	if name == None:
		return "request does not specify name query param", 400
	try:
		summary = recipeSummary(name)
	except Exception as err:
		print("exception is: {}".format(err.args))
		return err.args[0], 400
	else:
		print("summary is: {}".format(summary))
		return summary, 200

def getItem(itemName):
	for item in cookbook:
		if item["name"] == itemName:
			return item
	raise Exception("Item: {} does not exist".format(itemName))
    
def recipeSummary(recipeName):
	result = {
		"name": recipeName,
		"cookTime": 0,
		"ingredients": []
	}
	# if recipe name doesn't exist, then throw an error
	recipe = next(filter(lambda item: item["name"] == recipeName and item["type"] == "recipe", cookbook), None)
	if recipe == None:
		raise Exception(f"recipe with name: {recipeName} does not exist")
    
    # go through requireditems
	for item in recipe["requiredItems"]:
		itemObj = getItem(item["name"])
        # if its an ingredient
		if itemObj["type"] == "ingredient":
			ingredient = itemObj
     		# if exists, then add the ingredient to the summary (if ingredient exists, already, then just increment the quantity), and add the quantity * cookTime to the total cookTime
			summaryIngredient = next(filter(lambda ing: ing["name"] == ingredient["name"], result["ingredients"]), None)
			if summaryIngredient:
				summaryIngredient["quantity"] += item["quantity"]
			else:
				result["ingredients"].append({
					"name": item["name"],
					"quantity": item["quantity"]
				})
			result["cookTime"] += item["quantity"] * ingredient["cookTime"]
		# if its a recipe then get the recipeSummary for this recipe, then add the cookTime, and the base ingredients to the list (if base ingredients exist already, then just increment the quantity)
		if itemObj["type"] == "recipe":
			subRecipeSummary = recipeSummary(item["name"])
			for ingredient in subRecipeSummary["ingredients"]:
				summaryIngredient = next(filter(lambda ing: ing["name"] == ingredient["name"], result["ingredients"]), None)
				if summaryIngredient:
					summaryIngredient["quantity"] += ingredient["quantity"]
				else:
					result["ingredients"].append({
						"name": ingredient["name"],
						"quantity": ingredient["quantity"]
                    })
			result["cookTime"] += subRecipeSummary["cookTime"]
	return result


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
