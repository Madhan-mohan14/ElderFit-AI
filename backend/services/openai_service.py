import os
from openai import OpenAI
from backend.config import Config

class OpenAIService:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        # Only initialize client if API key is present
        if self.api_key and self.api_key.strip():
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.model = "gpt-4-turbo-preview"
                self.is_configured = True
            except Exception:
                self.client = None
                self.is_configured = False
        else:
            self.client = None
            self.is_configured = False
    
    async def generate_plan_explanation(self, plan_data: dict, user_context: dict) -> str:
        """Generate explanation for why a plan was selected"""
        prompt = f"""
        As an ElderFit AI wellness coach, explain why this daily wellness plan was created for a {user_context.get('age')} year old user.
        
        User Context:
        - Mood: {user_context.get('mood')}
        - Appetite: {user_context.get('appetite')}
        - Energy Level: {user_context.get('energy', 'medium')}
        
        Daily Plan:
        - Breakfast: {plan_data.get('breakfast', {}).get('name')} ({plan_data.get('breakfast', {}).get('calories')} cal)
        - Lunch: {plan_data.get('lunch', {}).get('name')} ({plan_data.get('lunch', {}).get('calories')} cal)
        - Dinner: {plan_data.get('dinner', {}).get('name')} ({plan_data.get('dinner', {}).get('calories')} cal)
        - Total Calories: {plan_data.get('total_calories')}
        - Exercises: {len(plan_data.get('exercises', []))} gentle exercise videos
        
        Provide a warm, friendly explanation (2-3 sentences) in {user_context.get('language', 'English')} that:
        1. Acknowledges their current mood and energy
        2. Explains why these specific meals and exercises are beneficial
        3. Encourages gentle adherence without pressure
        
        Remember: This is wellness coaching only, not medical advice.
        """
        
        # Check if OpenAI is configured
        if not self.is_configured or not self.client:
            # Generate a personalized fallback explanation
            mood = user_context.get('mood', 'neutral')
            energy = user_context.get('energy', 'medium')
            age = user_context.get('age', 70)
            
            explanations = {
                'happy': f"Your wellness plan is designed to maintain your positive energy and support your active lifestyle at {age}.",
                'tired': f"Your plan includes gentle, restorative options that respect your current energy levels while still providing essential nutrition.",
                'stressed': f"Your plan focuses on calming, nourishing foods and gentle movements to help you feel more balanced and relaxed.",
                'low': f"Your plan includes nutrient-dense, easy-to-prepare meals and gentle exercises to help boost your energy naturally.",
                'neutral': f"Your personalized wellness plan has been created to support your health and wellbeing at {age}."
            }
            return explanations.get(mood.lower(), explanations['neutral'])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a compassionate wellness coach for elderly users (60-85 years). Always be warm, encouraging, and clear. Never provide medical diagnosis or treatment advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"OpenAI API error: {str(e)}")
            return f"Your personalized wellness plan has been created based on your current mood, appetite, and energy levels."
    
    async def chat_response(self, message: str, user_context: dict, language: str = "en") -> str:
        """Generate chatbot response about nutrition and wellness"""
        lang_map = {"en": "English", "hi": "Hindi", "te": "Telugu"}
        lang_name = lang_map.get(language, "English")
        
        prompt = f"""
        User Message (in {lang_name}): {message}
        
        User Context:
        - Age: {user_context.get('age')} years
        - Mood: {user_context.get('mood', 'neutral')}
        
        Respond in {lang_name} about:
        - Nutrition and healthy eating for elderly
        - Gentle exercise and movement
        - General wellness tips
        
        DO NOT provide:
        - Medical diagnosis
        - Treatment advice
        - Medication recommendations
        
        Be warm, friendly, and encouraging. Keep responses concise (2-3 sentences max).
        """
        
        # Check if OpenAI is configured
        if not self.is_configured or not self.client:
            # Provide intelligent fallback responses based on the question
            return self._get_intelligent_fallback(message, user_context, language)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are ElderFit AI, a wellness assistant for elderly users (60-85 years). Respond in {lang_name}. Be warm, supportive, and never provide medical advice. Give specific, practical nutrition and wellness advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"OpenAI API error: {str(e)}")
            # Use intelligent fallback instead of generic message
            return self._get_intelligent_fallback(message, user_context, language)
    
    def _get_intelligent_fallback(self, message: str, user_context: dict, language: str = "en") -> str:
        """Provide intelligent fallback responses based on common nutrition questions"""
        message_lower = message.lower().strip()
        age = user_context.get('age', 70)
        
        # Helper function to check if any keyword is in the message
        def has_keyword(keywords):
            return any(keyword in message_lower for keyword in keywords)
        
        # English responses
        if language == "en":
            # Foods with specific ingredients (banana, apple, etc.) - check these first
            if has_keyword(['banana', 'bananas', 'with banana']):
                return f"Great question! Here are some healthy foods you can make with bananas at age {age}: Banana oatmeal (mashed banana in oatmeal with nuts), banana smoothie (banana, yogurt, and berries), banana whole grain pancakes, banana with peanut butter on whole grain toast, or a simple banana with a handful of almonds. Bananas are rich in potassium, fiber, and natural energy - perfect for seniors!"
            
            if has_keyword(['apple', 'apples', 'with apple']):
                return f"Apples are excellent for seniors! Try these at age {age}: Apple slices with almond butter, baked apples with cinnamon, apple oatmeal, apple salad with walnuts, or simply a fresh apple as a snack. Apples provide fiber, vitamin C, and are easy to chew when sliced. They're great for digestion and heart health!"
            
            if has_keyword(['egg', 'eggs', 'with egg']):
                return f"Eggs are a wonderful protein source! At age {age}, try: Scrambled eggs with vegetables, soft-boiled eggs with whole grain toast, vegetable omelet, or egg salad with whole grain crackers. Eggs provide high-quality protein, vitamin D, and are easy to prepare. Make sure they're fully cooked for safety."
            
            if has_keyword(['chicken', 'with chicken']):
                return f"Chicken is a great lean protein! For age {age}, try: Grilled or baked chicken breast with steamed vegetables, chicken soup with vegetables and whole grain noodles, chicken salad with mixed greens, or chicken stir-fry with colorful vegetables. Keep it well-cooked, tender, and easy to chew. Remove skin to reduce fat."
            
            # More ingredient-specific questions
            if has_keyword(['yogurt', 'yoghurt']):
                return f"Yogurt is excellent for seniors! At age {age}, try: Greek yogurt with fresh berries and nuts, yogurt parfait with granola, yogurt smoothie with banana, or plain yogurt as a side with meals. Yogurt provides protein, calcium, and probiotics for gut health. Choose plain or low-sugar varieties."
            
            if has_keyword(['oatmeal', 'oats', 'porridge']):
                return f"Oatmeal is a perfect breakfast for seniors! At age {age}, try: Oatmeal with fruits (bananas, berries, apples), oatmeal with nuts and a drizzle of honey, or savory oatmeal with vegetables. Oatmeal provides fiber, helps with digestion, and keeps you full. It's easy to chew and gentle on the stomach."
            
            if has_keyword(['fish', 'salmon', 'tuna', 'cod', 'tilapia']):
                return f"Fish is excellent for heart and brain health! At age {age}, try: Baked or grilled fish (salmon, cod, tilapia) with steamed vegetables, fish soup, or fish with whole grain rice. Fish provides omega-3 fatty acids, high-quality protein, and is easy to digest. Aim for 2-3 servings per week."
            
            if has_keyword(['vegetable', 'vegetables', 'veggie', 'veggies']):
                return f"Vegetables are essential for seniors! At age {age}, include: Steamed or roasted vegetables (broccoli, carrots, green beans), vegetable soup, salads with mixed greens, or stir-fried vegetables. They provide fiber, vitamins, and antioxidants. Cook them until tender for easy chewing. Aim for 3-5 servings daily."
            
            if has_keyword(['fruit', 'fruits', 'berries', 'berry']):
                return f"Fruits are wonderful for seniors! At age {age}, enjoy: Fresh fruits (apples, bananas, berries, oranges), fruit salad, smoothies, or fruit with yogurt. Fruits provide vitamins, fiber, and natural energy. Choose soft, ripe fruits that are easy to chew. Aim for 2-3 servings daily."
            
            # Lunch-related questions
            if has_keyword(['lunch', 'lunchtime', 'midday meal', 'noon meal', 'what for lunch']):
                return f"For lunch at age {age}, I recommend: A balanced plate with lean protein (like grilled chicken, fish, or lentils), whole grains (brown rice or quinoa), and plenty of vegetables. Good options include: vegetable soup with whole grain bread, a salad with chickpeas and olive oil dressing, or steamed vegetables with a small portion of lean meat. These provide essential nutrients, fiber, and are easy to digest."
            
            # Breakfast questions
            if has_keyword(['breakfast', 'morning meal', 'first meal', 'what for breakfast']):
                return f"For breakfast at age {age}, I suggest: Oatmeal with fruits and nuts, whole grain toast with avocado, or Greek yogurt with berries. These provide sustained energy, fiber, and important nutrients like calcium and protein. Avoid sugary cereals and opt for whole foods that are gentle on digestion."
            
            # Dinner questions
            if has_keyword(['dinner', 'evening meal', 'supper', 'what for dinner']):
                return f"For dinner at age {age}, consider: Light, easily digestible meals like baked fish with steamed vegetables, lentil soup with whole grain bread, or a vegetable stir-fry with tofu. Keep it lighter than lunch to aid digestion before sleep. Include a source of protein and plenty of colorful vegetables."
            
            # Snack questions
            if has_keyword(['snack', 'snacks', 'between meals']):
                return f"For healthy snacks at age {age}, try: Fresh fruit (apple slices, berries, banana), a handful of nuts (almonds, walnuts), Greek yogurt, whole grain crackers with hummus, or a small portion of cottage cheese. These provide nutrients without being too heavy. Aim for snacks that combine protein and fiber."
            
            # Protein questions
            if has_keyword(['protein', 'proteins', 'protein source']):
                return f"Good protein sources for age {age} include: Lean meats (chicken, turkey, fish), eggs, dairy (Greek yogurt, cottage cheese), legumes (lentils, beans, chickpeas), and nuts. Aim for protein at each meal to maintain muscle mass. Fish like salmon also provide omega-3 fatty acids for heart and brain health."
            
            # Fiber questions
            if has_keyword(['fiber', 'fibre', 'constipation', 'digestion']):
                return f"For good fiber intake at age {age}, include: Whole grains (oats, brown rice, whole grain bread), fruits (berries, apples, pears), vegetables (broccoli, carrots, leafy greens), and legumes (beans, lentils). Aim for 25-30 grams daily. Drink plenty of water with high-fiber foods to aid digestion and prevent constipation."
            
            # Calcium questions
            if has_keyword(['calcium', 'bones', 'bone health', 'osteoporosis']):
                return f"For strong bones at age {age}, include calcium-rich foods: Dairy products (milk, yogurt, cheese), leafy green vegetables (spinach, kale), fortified foods (cereals, orange juice), and fish with edible bones (sardines, salmon). Aim for 1200mg daily. Pair with vitamin D (from sunlight or supplements) for better absorption."
            
            # General nutrition questions
            if has_keyword(['healthy', 'nutrition', 'nutritious', 'good food', 'what to eat', 'healthy eating']):
                return f"At age {age}, focus on: Whole grains, lean proteins (fish, chicken, beans), plenty of fruits and vegetables (aim for 5 servings daily), healthy fats (olive oil, nuts), and stay hydrated with 6-8 glasses of water. Include calcium-rich foods like dairy or leafy greens for bone health. Keep meals simple, well-cooked, and easy to chew."
            
            # Exercise questions
            if has_keyword(['exercise', 'workout', 'physical activity', 'movement', 'fitness']):
                return f"At age {age}, gentle exercises are best: 10-20 minutes of walking daily, chair yoga, gentle stretching, or tai chi. These improve balance, flexibility, and strength while being safe for your joints. Start slowly and listen to your body. Even 5-10 minutes daily makes a difference!"
            
            # Hydration questions
            if has_keyword(['water', 'hydration', 'drink', 'thirsty', 'dehydrated']):
                return f"Staying hydrated is crucial at age {age}! Aim for 6-8 glasses (1.5-2 liters) of water daily. Good options include: Plain water, herbal teas, water with lemon, or diluted fruit juice. Include water-rich foods like cucumbers, watermelon, and soups. Drink throughout the day, not just when thirsty."
            
            # Weight questions
            if has_keyword(['weight', 'lose weight', 'gain weight', 'maintain weight']):
                return f"At age {age}, focus on maintaining a healthy weight through: Balanced meals with appropriate portions, regular gentle exercise, staying hydrated, and eating nutrient-dense foods. Avoid extreme diets. If you need to adjust weight, consult with a healthcare provider for personalized guidance."
            
            # Simple greetings - provide helpful starter
            if has_keyword(['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'greetings']):
                return f"Hello! I'm here to help with your nutrition and wellness questions. At age {age}, I can help you with meal planning, healthy food choices, exercise recommendations, and general wellness tips. What would you like to know about today?"
            
            # Default helpful response with suggestions
            return f"I'm here to help with nutrition and wellness questions. At age {age}, I can help you with: meal ideas (breakfast, lunch, dinner, snacks), foods with specific ingredients (like 'foods with banana'), protein sources, fiber-rich foods, exercise recommendations, and hydration tips. What specific question do you have?"
        
        # Hindi responses
        elif language == "hi":
            if any(word in message_lower for word in ['lunch', 'दोपहर', 'भोजन']):
                return f"{age} साल की उम्र में दोपहर के भोजन के लिए, मैं सुझाव देता हूं: संतुलित प्लेट जिसमें दुबला प्रोटीन (ग्रिल्ड चिकन, मछली, या दाल), साबुत अनाज, और बहुत सारी सब्जियां हों। अच्छे विकल्पों में शामिल हैं: सब्जी का सूप, सलाद, या उबली हुई सब्जियां।"
            return f"मैं पोषण और कल्याण प्रश्नों में मदद करने के लिए यहाँ हूँ। {age} साल की उम्र में, संतुलित भोजन, फल, सब्जियां, और हल्की शारीरिक गतिविधि पर ध्यान दें।"
        
        # Telugu responses
        elif language == "te":
            if any(word in message_lower for word in ['lunch', 'మధ్యాహ్న', 'భోజనం']):
                return f"{age} సంవత్సరాల వయస్సులో మధ్యాహ్న భోజనానికి, నేను సిఫార్సు చేస్తున్నాను: తక్కువ కొవ్వు ప్రోటీన్, పూర్తి ధాన్యాలు, మరియు చాలా కూరగాయలతో సమతుల్య ప్లేట్. మంచి ఎంపికలలో కూరగాయల సూప్, సలాడ్, లేదా ఆవిరితో వండిన కూరగాయలు ఉన్నాయి."
            return f"నేను పోషకాహారం మరియు ఆరోగ్య ప్రశ్నలకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను. {age} సంవత్సరాల వయస్సులో, సమతుల్య భోజనం, పళ్లు, కూరగాయలు మరియు సున్నితమైన శారీరక కార్యకలాపాలపై దృష్టి పెట్టండి."
        
        # Default English
        return f"I'm here to help with nutrition and wellness questions. At age {age}, focus on balanced meals with plenty of fruits, vegetables, whole grains, and lean proteins. Stay hydrated and engage in gentle daily movement."

