import React, { useState } from 'react'
import { Card } from './ui/Card'
import { useNavigate } from 'react-router-dom'
import { Smile, Meh, Frown, AlertCircle, Coffee } from 'lucide-react'
import api from '../utils/api'

const CheckInPanel = ({ userProfile, setCurrentPlan, language }) => {
  const navigate = useNavigate()
  const [mood, setMood] = useState(null)
  const [appetite, setAppetite] = useState(50)
  const [adherence, setAdherence] = useState(80)
  const [energy, setEnergy] = useState('medium')
  const [loading, setLoading] = useState(false)

  const moods = [
    { id: 'happy', label: 'Happy', icon: Smile, color: 'text-yellow-500' },
    { id: 'neutral', label: 'Neutral', icon: Meh, color: 'text-gray-500' },
    { id: 'low', label: 'Low', icon: Frown, color: 'text-blue-500' },
    { id: 'stressed', label: 'Stressed', icon: AlertCircle, color: 'text-red-500' },
    { id: 'tired', label: 'Tired', icon: Coffee, color: 'text-orange-500' },
  ]

  const handleSubmit = async () => {
    if (!mood) {
      alert('Please select your mood')
      return
    }

    // Check if user profile exists
    if (!userProfile || !userProfile.age) {
      alert('Please create your user profile first from the Dashboard')
      navigate('/dashboard')
      return
    }

    setLoading(true)
    try {
      const checkInData = {
        mood,
        appetite: appetite < 33 ? 'low' : appetite < 66 ? 'normal' : 'high',
        yesterday_adherence: adherence,
        energy_level: energy
      }

      // Ensure all required fields are present with proper types
      const requestData = {
        age: parseInt(userProfile.age) || 70,
        allergies: Array.isArray(userProfile.allergies) ? userProfile.allergies : [],
        diet_type: userProfile.diet_type || 'balanced',
        medical_conditions: Array.isArray(userProfile.medical_conditions) ? userProfile.medical_conditions : [],
        mood: mood, // Already validated (happy, neutral, low, stressed, tired)
        appetite: checkInData.appetite, // low, normal, high
        yesterday_adherence: parseFloat(adherence) || 80,
        energy_level: energy // low, medium, high
      }
      
      // Validate age range
      if (requestData.age < 45 || requestData.age > 90) {
        alert('Age must be between 45 and 90. Please update your profile.')
        navigate('/dashboard')
        return
      }
      
      // Log the request for debugging
      console.log('Sending plan generation request:', JSON.stringify(requestData, null, 2))
      
      // Use a longer timeout for plan generation (60 seconds)
      const response = await api.post(`/check-in/generate-plan?language=${language}`, requestData, {
        timeout: 60000 // 60 seconds for plan generation
      })

      // Log the response for debugging
      console.log('Plan generation response:', response)
      console.log('Response data:', response.data)
      console.log('Response structure:', {
        hasPlan: !!response.data?.plan,
        hasExercises: !!response.data?.plan?.exercises,
        exerciseCount: response.data?.plan?.exercises?.length || 0,
        hasMeals: !!response.data?.plan?.meals,
        fullKeys: Object.keys(response.data || {})
      })

      // Ensure we have the plan data
      if (!response.data) {
        throw new Error('No response data received from server')
      }
      
      if (!response.data.plan) {
        console.error('Response missing plan data:', response.data)
        throw new Error('Invalid response from server: plan data missing. Response: ' + JSON.stringify(response.data))
      }

      // Set the plan and wait for state update
      console.log('Setting current plan...')
      setCurrentPlan(response.data)
      
      // Use a small delay to ensure state is updated and persisted before navigation
      await new Promise(resolve => setTimeout(resolve, 150))
      
      console.log('Navigating to plan page...')
      navigate('/plan')
    } catch (error) {
      console.error('Error generating plan:', error)
      console.error('Error type:', error.constructor.name)
      console.error('Error response:', error.response)
      console.error('Error response data:', error.response?.data)
      console.error('Error response status:', error.response?.status)
      console.error('Error message:', error.message)
      console.error('Error stack:', error.stack)
      
      let errorMessage = 'Error generating plan. Please try again.'
      
      if (error.response) {
        // Server responded with error
        const errorData = error.response.data
        console.error('Error data details:', JSON.stringify(errorData, null, 2))
        
        if (error.response.status === 422) {
          // Validation error - show user-friendly message
          const message = errorData?.message || errorData?.detail
          if (message) {
            errorMessage = message
          } else {
            const details = errorData?.details
            if (Array.isArray(details)) {
              const fieldErrors = details.map(d => {
                const field = d.loc?.join('.') || 'field'
                return `${field}: ${d.msg || d}`
              }).join(', ')
              errorMessage = `Validation error: ${fieldErrors}`
            } else {
              errorMessage = 'Invalid input data. Please check all fields are filled correctly and try again.'
            }
          }
          console.error('Validation error details:', errorData)
          
          // If age is missing, redirect to profile
          if (errorData?.detail?.includes('age') || errorData?.message?.includes('age')) {
            errorMessage += '\n\nPlease create your user profile first.'
            setTimeout(() => navigate('/dashboard'), 2000)
          }
        } else if (errorData?.message) {
          errorMessage = errorData.message
        } else if (errorData?.detail) {
          errorMessage = `Error: ${errorData.detail}`
        } else if (error.response.status === 500) {
          // Show the actual error message from backend
          const detail = errorData?.detail || errorData?.message || errorData?.error
          if (detail) {
            errorMessage = detail
          } else {
            errorMessage = 'Server error. Please check if all API keys are configured in the backend and check the console for details.'
          }
        }
      } else if (error.backendNotRunning) {
        errorMessage = 'Backend server is not running. Please start it first.'
      } else if (error.message) {
        // Use the error message from the backend if available
        errorMessage = error.message
      }
      
      console.error('Full error details:', error)
      console.error('Error response status:', error.response?.status)
      console.error('Error response data:', JSON.stringify(error.response?.data, null, 2))
      
      // Show more detailed error in development
      if (import.meta.env.DEV) {
        console.error('Complete error object:', {
          message: error.message,
          response: error.response,
          request: error.request,
          config: error.config
        })
      }
      
      alert(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 w-full px-4">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Daily Check-In</h1>
        <p className="text-gray-600 mt-2">How are you feeling today?</p>
      </div>

      <Card>
        <h2 className="text-xl font-semibold mb-6">How is your mood today?</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {moods.map((m) => {
            const Icon = m.icon
            return (
              <button
                key={m.id}
                onClick={() => setMood(m.id)}
                className={`p-6 rounded-xl border-2 transition-all ${
                  mood === m.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon className={`w-12 h-12 mx-auto mb-2 ${m.color}`} />
                <p className="font-medium text-gray-700">{m.label}</p>
              </button>
            )
          })}
        </div>
      </Card>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Appetite Level</h2>
        <div className="space-y-4">
          <input
            type="range"
            min="0"
            max="100"
            value={appetite}
            onChange={(e) => setAppetite(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div className="flex justify-between text-sm text-gray-600">
            <span>Low</span>
            <span className="font-medium text-primary-600">{appetite}%</span>
            <span>High</span>
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Energy Level</h2>
        <div className="grid grid-cols-3 gap-4">
          {['low', 'medium', 'high'].map((level) => (
            <button
              key={level}
              onClick={() => setEnergy(level)}
              className={`p-4 rounded-lg border-2 capitalize transition-all ${
                energy === level
                  ? 'border-primary-500 bg-primary-50 text-primary-700 font-medium'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Yesterday's Plan Adherence</h2>
        <div className="space-y-4">
          <input
            type="range"
            min="0"
            max="100"
            value={adherence}
            onChange={(e) => setAdherence(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div className="flex justify-between text-sm text-gray-600">
            <span>0%</span>
            <span className="font-medium text-primary-600">{adherence}%</span>
            <span>100%</span>
          </div>
        </div>
      </Card>

      <button
        onClick={handleSubmit}
        disabled={loading || !mood}
        className="w-full bg-primary-600 text-white py-4 rounded-lg font-medium text-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Generating Your Plan...' : 'Generate Today\'s Plan'}
      </button>
    </div>
  )
}

export default CheckInPanel

