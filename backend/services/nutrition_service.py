import requests
from typing import List, Dict, Optional
from backend.config import Config
from backend.models.schemas import MealItem

class NutritionService:
    """Abstraction layer for nutrition APIs - currently uses USDA FoodData Central"""
    
    def __init__(self):
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1"
        self.api_key = Config.USDA_API_KEY
    
    async def search_food(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for foods in USDA database"""
        try:
            url = f"{self.usda_base_url}/foods/search"
            params = {
                "api_key": self.api_key,
                "query": query,
                "pageSize": limit,
                "dataType": ["Foundation", "SR Legacy"]
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("foods", [])
        except Exception as e:
            print(f"USDA API Error: {e}")
            # Return fallback data
            return self._get_fallback_foods(query)
    
    def _get_fallback_foods(self, query: str) -> List[Dict]:
        """Fallback food database for common elder-friendly meals"""
        fallback_db = {
            "oatmeal": {
                "description": "Oatmeal with fruits",
                "calories": 150,
                "protein": 5,
                "carbs": 27,
                "fat": 3,
                "fiber": 4,
                "calcium": 20
            },
            "soup": {
                "description": "Vegetable soup",
                "calories": 100,
                "protein": 3,
                "carbs": 15,
                "fat": 2,
                "fiber": 3,
                "calcium": 30
            },
            "rice": {
                "description": "Steamed rice with vegetables",
                "calories": 200,
                "protein": 4,
                "carbs": 45,
                "fat": 1,
                "fiber": 2,
                "calcium": 15
            },
            "chicken": {
                "description": "Boiled chicken breast",
                "calories": 165,
                "protein": 31,
                "carbs": 0,
                "fat": 3.6,
                "fiber": 0,
                "calcium": 15
            },
            "yogurt": {
                "description": "Plain yogurt",
                "calories": 100,
                "protein": 10,
                "carbs": 8,
                "fat": 3,
                "fiber": 0,
                "calcium": 200
            },
            "banana": {
                "description": "Banana",
                "calories": 105,
                "protein": 1,
                "carbs": 27,
                "fat": 0.4,
                "fiber": 3,
                "calcium": 6
            }
        }
        
        query_lower = query.lower()
        for key, value in fallback_db.items():
            if key in query_lower:
                return [{
                    "fdcId": hash(key),
                    "description": value["description"],
                    "foodNutrients": [
                        {"nutrientName": "Energy", "value": value["calories"]},
                        {"nutrientName": "Protein", "value": value["protein"]},
                        {"nutrientName": "Carbohydrate, by difference", "value": value["carbs"]},
                        {"nutrientName": "Total lipid (fat)", "value": value["fat"]},
                        {"nutrientName": "Fiber, total dietary", "value": value["fiber"]},
                        {"nutrientName": "Calcium, Ca", "value": value["calcium"]}
                    ]
                }]
        return []
    
    def _parse_usda_food(self, food_data: Dict) -> Optional[MealItem]:
        """Parse USDA food data into MealItem"""
        try:
            nutrients = {item.get("nutrientName", ""): item.get("value", 0) 
                        for item in food_data.get("foodNutrients", [])}
            
            return MealItem(
                name=food_data.get("description", "Unknown"),
                calories=nutrients.get("Energy", 0),
                protein=nutrients.get("Protein", 0),
                carbs=nutrients.get("Carbohydrate, by difference", 0),
                fat=nutrients.get("Total lipid (fat)", 0),
                fiber=nutrients.get("Fiber, total dietary", 0),
                calcium=nutrients.get("Calcium, Ca", 0),
                preparation_time=15,  # Default estimate
                simplicity_score=0.7  # Default
            )
        except Exception:
            return None
    
    async def get_elder_friendly_meal(self, meal_type: str, preferences: Dict) -> MealItem:
        """Get elder-friendly meal suggestion"""
        # Map meal types to search queries
        meal_queries = {
            "breakfast": ["oatmeal", "porridge", "soft eggs", "yogurt"],
            "lunch": ["soup", "steamed vegetables", "soft rice"],
            "dinner": ["soup", "steamed vegetables", "soft chicken"],
            "snack": ["banana", "yogurt", "soft fruits"]
        }
        
        queries = meal_queries.get(meal_type, ["balanced meal"])
        query = queries[0]  # Use first query
        
        # Adjust based on mood and appetite
        if preferences.get("mood") == "tired":
            query = "soup" if meal_type in ["lunch", "dinner"] else query
        if preferences.get("appetite") == "low":
            query = "soup" if meal_type in ["lunch", "dinner"] else "yogurt"
        
        foods = await self.search_food(query, limit=5)
        if foods:
            parsed = self._parse_usda_food(foods[0])
            if parsed:
                return parsed
        
        # Fallback to default meal
        return self._get_default_meal(meal_type)
    
    def _get_default_meal(self, meal_type: str) -> MealItem:
        """Default meal items for elders"""
        defaults = {
            "breakfast": MealItem(
                name="Oatmeal with fruits and yogurt",
                calories=250,
                protein=10,
                carbs=45,
                fat=5,
                fiber=6,
                calcium=150,
                preparation_time=10,
                simplicity_score=0.8
            ),
            "lunch": MealItem(
                name="Vegetable soup with soft rice",
                calories=350,
                protein=8,
                carbs=55,
                fat=5,
                fiber=8,
                calcium=100,
                preparation_time=20,
                simplicity_score=0.7
            ),
            "dinner": MealItem(
                name="Steamed vegetables with soft chicken",
                calories=400,
                protein=25,
                carbs=30,
                fat=10,
                fiber=6,
                calcium=80,
                preparation_time=25,
                simplicity_score=0.6
            ),
            "snack": MealItem(
                name="Banana with yogurt",
                calories=150,
                protein=5,
                carbs=28,
                fat=2,
                fiber=4,
                calcium=120,
                preparation_time=5,
                simplicity_score=0.9
            )
        }
        return defaults.get(meal_type, defaults["breakfast"])

