import React from 'react'
import { Card } from './ui/Card'
import { Clock, Utensils, Droplet, Dumbbell, Play } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const PlanExecution = ({ plan, language }) => {
  const navigate = useNavigate()

  // Debug logging
  React.useEffect(() => {
    console.log('PlanExecution - Received plan:', plan)
    if (plan) {
      console.log('Plan structure:', {
        hasPlan: !!plan.plan,
        hasMeals: !!plan.plan?.meals,
        hasExercises: !!plan.plan?.exercises,
        exerciseCount: plan.plan?.exercises?.length || 0
      })
    }
  }, [plan])

  if (!plan || !plan.plan) {
    return (
      <Card>
        <p className="text-gray-600">No plan available. Please complete your daily check-in first.</p>
        <p className="text-sm text-gray-500 mt-2">Debug: plan = {plan ? 'exists' : 'null'}, plan.plan = {plan?.plan ? 'exists' : 'null'}</p>
        <button
          onClick={() => navigate('/check-in')}
          className="mt-4 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
        >
          Go to Check-In
        </button>
      </Card>
    )
  }

  const meals = plan.plan.meals
  const exercises = plan.plan.exercises || []
  
  // Additional validation
  if (!meals) {
    console.error('Plan has no meals data:', plan)
    return (
      <Card>
        <p className="text-red-600">Error: Plan data is incomplete. Please try generating a new plan.</p>
        <button
          onClick={() => navigate('/check-in')}
          className="mt-4 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
        >
          Generate New Plan
        </button>
      </Card>
    )
  }

  return (
    <div className="space-y-6 w-full max-w-full overflow-x-hidden">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Today's Wellness Plan</h1>
        <p className="text-gray-600 mt-2">{plan.plan.reasoning || 'Your personalized plan for today'}</p>
      </div>

      {plan.plan.hydration_reminder && (
        <Card className="bg-blue-50 border-blue-200">
          <div className="flex items-center space-x-3">
            <Droplet className="w-6 h-6 text-blue-600" />
            <div>
              <p className="font-medium text-blue-900">Hydration Reminder</p>
              <p className="text-sm text-blue-700">Remember to drink 8 glasses of water today</p>
            </div>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Meals Section */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
            <Utensils className="w-6 h-6 mr-2" />
            Meals
          </h2>

          <MealCard
            meal={meals.breakfast}
            mealType="Breakfast"
            time="8:00 AM"
          />
          <MealCard
            meal={meals.lunch}
            mealType="Lunch"
            time="1:00 PM"
          />
          <MealCard
            meal={meals.dinner}
            mealType="Dinner"
            time="7:00 PM"
          />

          {meals.snacks && meals.snacks.length > 0 && (
            <Card>
              <h3 className="font-semibold mb-3">Snacks</h3>
              {meals.snacks.map((snack, idx) => (
                <MealCard key={idx} meal={snack} mealType="Snack" time="3:00 PM" small />
              ))}
            </Card>
          )}

          {/* Nutrition Summary */}
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100">
            <h3 className="font-semibold mb-4">Daily Nutrition Summary</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Total Calories</p>
                <p className="text-2xl font-bold text-purple-700">{Math.round(meals.total_calories)}</p>
              </div>
              <div>
                <p className="text-gray-600">Protein</p>
                <p className="text-2xl font-bold text-purple-700">{Math.round(meals.total_protein)}g</p>
              </div>
              <div>
                <p className="text-gray-600">Carbs</p>
                <p className="text-2xl font-bold text-purple-700">{Math.round(meals.total_carbs)}g</p>
              </div>
              <div>
                <p className="text-gray-600">Fat</p>
                <p className="text-2xl font-bold text-purple-700">{Math.round(meals.total_fat)}g</p>
              </div>
              <div>
                <p className="text-gray-600">Fiber</p>
                <p className="text-2xl font-bold text-purple-700">{Math.round(meals.total_fiber || 0)}g</p>
              </div>
              <div>
                <p className="text-gray-600">Calcium</p>
                <p className="text-2xl font-bold text-purple-700">{Math.round(meals.total_calcium || 0)}mg</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Exercises Section */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
            <Dumbbell className="w-6 h-6 mr-2" />
            Gentle Exercises
          </h2>

          {exercises.map((exercise, idx) => (
            <ExerciseCard key={idx} exercise={exercise} />
          ))}
        </div>
      </div>

      <div className="flex space-x-4">
        <button
          onClick={() => navigate('/decision-trace')}
          className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors"
        >
          View Decision Trace
        </button>
        <button
          onClick={() => navigate('/feedback')}
          className="flex-1 bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
        >
          Submit Feedback
        </button>
      </div>
    </div>
  )
}

const MealCard = ({ meal, mealType, time, small = false }) => {
  return (
    <Card className={small ? 'py-3' : ''}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className={`font-semibold ${small ? 'text-base' : 'text-lg'}`}>{mealType}</h3>
            <span className="text-sm text-gray-500 flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              {time}
            </span>
          </div>
          <p className={`font-medium text-gray-900 ${small ? 'text-sm' : 'text-base'}`}>{meal.name}</p>
          <div className={`flex flex-wrap gap-3 mt-2 ${small ? 'text-xs' : 'text-sm'} text-gray-600`}>
            <span>{Math.round(meal.calories)} cal</span>
            <span>{Math.round(meal.protein)}g protein</span>
            <span>{Math.round(meal.carbs)}g carbs</span>
            {meal.fiber && <span>{Math.round(meal.fiber)}g fiber</span>}
            {meal.calcium && <span>{Math.round(meal.calcium)}mg calcium</span>}
          </div>
          {meal.preparation_time && (
            <p className="text-xs text-gray-500 mt-2">
              Prep time: ~{meal.preparation_time} minutes
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}

const ExerciseCard = ({ exercise }) => {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <div className="flex space-x-4">
        <img
          src={exercise.thumbnail_url}
          alt={exercise.title}
          className="w-32 h-24 object-cover rounded-lg"
        />
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1">{exercise.title}</h3>
          <p className="text-sm text-gray-600 line-clamp-2 mb-2">{exercise.description}</p>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>{exercise.duration} min</span>
              <span>{exercise.channel_name}</span>
            </div>
            <a
              href={exercise.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 font-medium"
            >
              <Play className="w-4 h-4" />
              <span>Watch</span>
            </a>
          </div>
        </div>
      </div>
    </Card>
  )
}

export default PlanExecution

