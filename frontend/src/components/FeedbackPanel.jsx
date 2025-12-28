import React, { useState } from 'react'
import { Card } from './ui/Card'
import { useNavigate } from 'react-router-dom'
import { Check, X, Heart, HeartOff } from 'lucide-react'
import api from '../utils/api'

const FeedbackPanel = ({ plan }) => {
  const navigate = useNavigate()
  const [dietFollowed, setDietFollowed] = useState(80)
  const [exerciseCompleted, setExerciseCompleted] = useState(false)
  const [likedFoods, setLikedFoods] = useState([])
  const [dislikedFoods, setDislikedFoods] = useState([])
  const [likedVideos, setLikedVideos] = useState([])
  const [dislikedVideos, setDislikedVideos] = useState([])
  const [submitting, setSubmitting] = useState(false)

  if (!plan || !plan.plan) {
    return (
      <Card>
        <p className="text-gray-600">No plan available. Please complete your daily check-in first.</p>
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

  const toggleFoodPreference = (foodName, isLike) => {
    if (isLike) {
      setLikedFoods(prev => 
        prev.includes(foodName) 
          ? prev.filter(f => f !== foodName)
          : [...prev, foodName]
      )
      setDislikedFoods(prev => prev.filter(f => f !== foodName))
    } else {
      setDislikedFoods(prev => 
        prev.includes(foodName)
          ? prev.filter(f => f !== foodName)
          : [...prev, foodName]
      )
      setLikedFoods(prev => prev.filter(f => f !== foodName))
    }
  }

  const toggleVideoPreference = (videoId, isLike) => {
    if (isLike) {
      setLikedVideos(prev => 
        prev.includes(videoId)
          ? prev.filter(v => v !== videoId)
          : [...prev, videoId]
      )
      setDislikedVideos(prev => prev.filter(v => v !== videoId))
    } else {
      setDislikedVideos(prev => 
        prev.includes(videoId)
          ? prev.filter(v => v !== videoId)
          : [...prev, videoId]
      )
      setLikedVideos(prev => prev.filter(v => v !== videoId))
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const feedbackData = {
        plan_id: String(plan.plan_id || plan.plan?.date || '1'),
        diet_followed: parseFloat(dietFollowed),
        exercise_completed: exerciseCompleted,
        liked_foods: Array.isArray(likedFoods) ? likedFoods : [],
        disliked_foods: Array.isArray(dislikedFoods) ? dislikedFoods : [],
        liked_videos: Array.isArray(likedVideos) ? likedVideos : [],
        disliked_videos: Array.isArray(dislikedVideos) ? dislikedVideos : []
      }
      
      console.log('Submitting feedback:', feedbackData)
      const response = await api.post('/feedback', feedbackData)
      
      alert('Feedback submitted successfully! Thank you for helping us improve.')
      navigate('/dashboard')
    } catch (error) {
      console.error('Error submitting feedback:', error)
      let errorMessage = 'Error submitting feedback. Please try again.'
      
      if (error.response) {
        const errorData = error.response.data
        if (error.response.status === 422) {
          errorMessage = errorData?.message || errorData?.detail || 'Invalid feedback data. Please check all fields.'
        } else if (error.response.status === 400) {
          errorMessage = errorData?.detail || 'Invalid request. Please try again.'
        }
      } else if (error.backendNotRunning) {
        errorMessage = 'Backend server is not running. Please start it first.'
      }
      
      alert(errorMessage)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 w-full px-4">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">End of Day Feedback</h1>
        <p className="text-gray-600 mt-2">Help us improve your wellness plans</p>
      </div>

      <Card>
        <h2 className="text-xl font-semibold mb-4">How much of today's diet did you follow?</h2>
        <div className="space-y-4">
          <input
            type="range"
            min="0"
            max="100"
            value={dietFollowed}
            onChange={(e) => setDietFollowed(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div className="flex justify-between text-sm text-gray-600">
            <span>0%</span>
            <span className="font-medium text-primary-600">{dietFollowed}%</span>
            <span>100%</span>
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Did you complete the exercises?</h2>
        <div className="flex space-x-4">
          <button
            onClick={() => setExerciseCompleted(true)}
            className={`flex-1 py-3 rounded-lg border-2 transition-colors ${
              exerciseCompleted
                ? 'border-green-500 bg-green-50 text-green-700 font-medium'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Check className="w-5 h-5 mx-auto mb-1" />
            Yes
          </button>
          <button
            onClick={() => setExerciseCompleted(false)}
            className={`flex-1 py-3 rounded-lg border-2 transition-colors ${
              !exerciseCompleted
                ? 'border-red-500 bg-red-50 text-red-700 font-medium'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <X className="w-5 h-5 mx-auto mb-1" />
            No
          </button>
        </div>
      </Card>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Rate Today's Meals</h2>
        <div className="space-y-3">
          <MealFeedback
            meal={meals.breakfast}
            mealType="Breakfast"
            onToggle={toggleFoodPreference}
            likedFoods={likedFoods}
            dislikedFoods={dislikedFoods}
          />
          <MealFeedback
            meal={meals.lunch}
            mealType="Lunch"
            onToggle={toggleFoodPreference}
            likedFoods={likedFoods}
            dislikedFoods={dislikedFoods}
          />
          <MealFeedback
            meal={meals.dinner}
            mealType="Dinner"
            onToggle={toggleFoodPreference}
            likedFoods={likedFoods}
            dislikedFoods={dislikedFoods}
          />
        </div>
      </Card>

      {exercises.length > 0 && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Rate Today's Exercises</h2>
          <div className="space-y-3">
            {exercises.map((exercise) => (
              <VideoFeedback
                key={exercise.video_id}
                exercise={exercise}
                onToggle={toggleVideoPreference}
                likedVideos={likedVideos}
                dislikedVideos={dislikedVideos}
              />
            ))}
          </div>
        </Card>
      )}

      <button
        onClick={handleSubmit}
        disabled={submitting}
        className="w-full bg-primary-600 text-white py-4 rounded-lg font-medium text-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {submitting ? 'Submitting...' : 'Submit Feedback'}
      </button>
    </div>
  )
}

const MealFeedback = ({ meal, mealType, onToggle, likedFoods, dislikedFoods }) => {
  const isLiked = likedFoods.includes(meal.name)
  const isDisliked = dislikedFoods.includes(meal.name)

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div>
        <p className="font-medium text-gray-900">{mealType}: {meal.name}</p>
      </div>
      <div className="flex space-x-2">
        <button
          onClick={() => onToggle(meal.name, true)}
          className={`p-2 rounded-lg transition-colors ${
            isLiked
              ? 'bg-green-100 text-green-700'
              : 'bg-white text-gray-400 hover:text-green-600'
          }`}
        >
          <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
        </button>
        <button
          onClick={() => onToggle(meal.name, false)}
          className={`p-2 rounded-lg transition-colors ${
            isDisliked
              ? 'bg-red-100 text-red-700'
              : 'bg-white text-gray-400 hover:text-red-600'
          }`}
        >
          <HeartOff className={`w-5 h-5 ${isDisliked ? 'fill-current' : ''}`} />
        </button>
      </div>
    </div>
  )
}

const VideoFeedback = ({ exercise, onToggle, likedVideos, dislikedVideos }) => {
  const isLiked = likedVideos.includes(exercise.video_id)
  const isDisliked = dislikedVideos.includes(exercise.video_id)

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <img
          src={exercise.thumbnail_url}
          alt={exercise.title}
          className="w-16 h-12 object-cover rounded"
        />
        <div>
          <p className="font-medium text-gray-900 text-sm">{exercise.title}</p>
          <p className="text-xs text-gray-600">{exercise.duration} min</p>
        </div>
      </div>
      <div className="flex space-x-2">
        <button
          onClick={() => onToggle(exercise.video_id, true)}
          className={`p-2 rounded-lg transition-colors ${
            isLiked
              ? 'bg-green-100 text-green-700'
              : 'bg-white text-gray-400 hover:text-green-600'
          }`}
        >
          <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
        </button>
        <button
          onClick={() => onToggle(exercise.video_id, false)}
          className={`p-2 rounded-lg transition-colors ${
            isDisliked
              ? 'bg-red-100 text-red-700'
              : 'bg-white text-gray-400 hover:text-red-600'
          }`}
        >
          <HeartOff className={`w-5 h-5 ${isDisliked ? 'fill-current' : ''}`} />
        </button>
      </div>
    </div>
  )
}

export default FeedbackPanel

