import json
import requests
import random
from config import (OPENWEATHER_API_KEY, EDAMAM_APP_ID, EDAMAM_APP_KEY,
                    EDAMAM_NUTRITION_APP_ID, EDAMAM_NUTRITION_APP_KEY,
                    OPENWEATHER_ENDPOINT, EDAMAM_RECIPE_ENDPOINT, EDAMAM_NUTRITION_ENDPOINT)
from utils import validate_and_process_input


def welcome_user():
    print("Hello! Welcome to The Search Bar. Let's start.")


def get_weather_and_suggest_recipe():
    city = input("Enter your city to check the weather: ")
    weather_data = get_current_weather(city)
    if weather_data:
        print(
            f"Current weather in {city}: {weather_data['weather'][0]['description']}, {weather_data['main']['temp']}°C")
        return suggest_recipe_by_category(weather_data)
    else:
        print("Could not retrieve weather data. Proceeding with default recipe suggestions.")
        return None


def get_current_weather(city):
    url = f"{OPENWEATHER_ENDPOINT}?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def get_random_recipe(query):
    url = f"{EDAMAM_RECIPE_ENDPOINT}?q={query}&app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}&to=20"
    try:
        response = requests.get(url)
        response.raise_for_status()
        recipes = response.json()["hits"]
        if recipes:
            return random.choice(recipes)["recipe"]
        else:
            return None
    except requests.RequestException:
        return None


def suggest_recipe_by_category(weather_data):
    if not weather_data:
        return get_random_recipe("dessert")

    temp = weather_data["main"]["temp"]
    if temp < 10:
        return get_random_recipe("soup")
    elif temp > 25:
        return get_random_recipe("salad")
    else:
        return get_random_recipe("bake")


def get_user_ingredient_preferences():
    ingredients = input("Enter ingredients you have (separate by comma, e.g., tomatoes, cheese): ")
    return validate_and_process_input(ingredients)


def get_recipes(ingredients):
    url = f"{EDAMAM_RECIPE_ENDPOINT}?q={ingredients}&app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["hits"]
    except requests.RequestException:
        print("There was an error with the recipe request.")
        return []


def save_ingredients_to_file(recipe, file_name="ingredients.txt"):
    with open(file_name, "w") as file:
        file.write(f"Ingredients for {recipe['label']}:\n")
        for ingredient in recipe['ingredientLines']:
            file.write(f"{ingredient}\n")


def get_nutrition_data(ingredients):
    headers = {"Content-Type": "application/json"}
    payload = {"ingr": ingredients}
    try:
        response = requests.post(EDAMAM_NUTRITION_ENDPOINT, headers=headers, json=payload,
                                 auth=(EDAMAM_NUTRITION_APP_ID, EDAMAM_NUTRITION_APP_KEY))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching nutrition data: {e}")
        return {}


def handle_recipe_suggestion_by_weather():
    suggested_recipe = get_weather_and_suggest_recipe()
    if suggested_recipe:
        print(f"Suggested Recipe: {suggested_recipe['label']}")
        user_interest = input("Are you interested in this recipe? (yes/no): ")
        if user_interest.lower() == 'yes':
            display_recipe_details(suggested_recipe)
            handle_nutrition_data(suggested_recipe)
            prompt_save_ingredients_to_file(suggested_recipe)
        else:
            handle_user_provided_ingredients()
    else:
        handle_user_provided_ingredients()


def handle_user_provided_ingredients():
    ingredients = get_user_ingredient_preferences()
    recipes = get_recipes(ingredients)
    if recipes:
        selected_recipe = display_recipes_and_get_selection(recipes)
        display_recipe_details(selected_recipe)
        handle_nutrition_data(selected_recipe)
        prompt_save_ingredients_to_file(selected_recipe)
    else:
        print("No recipes found with the given ingredients.")


def display_recipes_and_get_selection(recipes):
    for i, recipe in enumerate(recipes):
        print(f"{i + 1}: Recipe Name: {recipe['recipe']['label']}")
    choice = int(input("\nChoose the recipe number for more details: "))
    return recipes[choice - 1]['recipe']


def display_recipe_details(recipe):
    print(f"Recipe: {recipe['label']}")
    print(f"URL: {recipe['url']}")
    print(f"Ingredients: {recipe['ingredientLines']}")


def handle_nutrition_data(recipe):
    get_nutrition = input("Would you like to see the nutrition data for this recipe? (yes/no): ")
    if get_nutrition.lower() == 'yes':
        ingredients_for_nutrition = recipe['ingredientLines']
        nutrition_data = get_nutrition_data(ingredients_for_nutrition)
        if nutrition_data:
            print(json.dumps(nutrition_data, indent=2))
        else:
            print("Nutrition data not available.")


def prompt_save_ingredients_to_file(recipe):
    save_to_file = input("Would you like to save the ingredients to a file? (yes/no): ")
    if save_to_file.lower() == 'yes':
        save_ingredients_to_file(recipe)
        print("Ingredients list saved to file.")


def main():
    welcome_user()
    handle_recipe_suggestion_by_weather()


if __name__ == "__main__":
    main()
