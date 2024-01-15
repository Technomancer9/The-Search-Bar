import unittest
from unittest.mock import patch, mock_open

from main import save_ingredients_to_file, get_recipes, get_random_recipe, get_nutrition_data
from utils import validate_and_process_input


class TestRecipeApp(unittest.TestCase):
    def setUp(self):
        self.mock_response_hits = {
            "hits": [{"recipe": {"label": "Test Recipe", "ingredientLines": ["1 apple", "2 bananas"]}}]
        }
        self.mock_response_no_hits = {
            "hits": []
        }

    @patch('requests.get')
    def test_get_recipes_with_results(self, mock_get):
        mock_get.return_value.json.return_value = self.mock_response_hits
        ingredients = 'apple'
        results = get_recipes(ingredients)
        self.assertTrue(all('recipe' in hit for hit in results))

    @patch('requests.get')
    def test_get_recipes_no_results(self, mock_get):
        mock_get.return_value.json.return_value = self.mock_response_no_hits
        ingredients = 'unknowningredient'
        results = get_recipes(ingredients)
        self.assertEqual(len(results), 0)

    def test_validate_and_process_input(self):
        self.assertEqual(validate_and_process_input("Apples, Milk, Sugar"), "apples, milk, sugar")
        self.assertEqual(validate_and_process_input("123"), "")
        self.assertEqual(validate_and_process_input("/*//*"), "")

    def test_save_ingredients_to_file(self):
        test_recipe = {
            'label': 'Test Recipe',
            'ingredientLines': ['1 apple', '2 bananas']
        }
        expected_output = "Ingredients for Test Recipe:\n1 apple\n2 bananas\n"

        m = mock_open()
        with patch("builtins.open", m):
            save_ingredients_to_file(test_recipe, "test.txt")

        m.assert_called_once_with("test.txt", "w")
        handle = m()

        handle.write.assert_any_call("Ingredients for Test Recipe:\n")
        handle.write.assert_any_call("1 apple\n")
        handle.write.assert_any_call("2 bananas\n")

    @patch('main.requests.post')
    def test_get_nutrition_data_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "calories": 100,
            "totalNutrients": {"FAT": {"quantity": 0.5}}
        }

        ingredients = ['1 apple', '2 bananas']
        result = get_nutrition_data(ingredients)
        self.assertEqual(result['calories'], 100)
        self.assertIn('FAT', result['totalNutrients'])

    @patch('main.requests.post')
    def test_get_nutrition_data_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"error": "Bad Request"}

        ingredients = ['1 apple', '2 bananas']
        result = get_nutrition_data(ingredients)
        self.assertEqual(result, {"error": "Bad Request"})

    @patch('main.requests.get')
    def test_get_random_recipe(self, mock_get):
        mock_get.return_value.json.return_value = {
            "hits": [{"recipe": {"label": "Test Chicken Recipe", "url": "http://example.com"}}]
        }
        query = "chicken"
        recipe = get_random_recipe(query)
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe['label'], "Test Chicken Recipe")
        self.assertEqual(recipe['url'], "http://example.com")




if __name__ == '__main__':
    unittest.main()