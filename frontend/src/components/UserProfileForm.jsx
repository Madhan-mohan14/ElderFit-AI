import React, { useState } from 'react'
import { Card } from './ui/Card'
import { AlertCircle } from 'lucide-react'
import api from '../utils/api'

const UserProfileForm = ({ setUserProfile }) => {
  const [formData, setFormData] = useState({
    age: '',
    allergies: '',
    diet_type: 'balanced',
    medical_conditions: ''
  })
  const [backendError, setBackendError] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const profile = {
      age: parseInt(formData.age),
      allergies: formData.allergies.split(',').map(a => a.trim()).filter(a => a),
      diet_type: formData.diet_type,
      medical_conditions: formData.medical_conditions.split(',').map(m => m.trim()).filter(m => m)
    }

    try {
      const response = await api.post('/users', profile)
      console.log('Profile created:', response.data)
      setUserProfile(profile)
      setBackendError(false)
    } catch (error) {
      console.error('Error creating profile:', error)
      setBackendError(true)
      if (error.backendNotRunning || error.code === 'ECONNREFUSED') {
        // Backend not running - show inline error
        return
      } else if (error.response) {
        // Server responded with error status
        alert(`Error: ${error.response.data?.detail || 'Failed to create profile'}`)
      } else {
        alert('Error creating profile. Please try again.')
      }
    }
  }

  return (
    <div className="max-w-2xl mx-auto w-full px-4">
      <Card>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to ElderFit AI</h1>
        <p className="text-gray-600 mb-6">Let's set up your wellness profile</p>

        {backendError && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="font-medium text-yellow-800">Backend server not running</p>
                <p className="text-sm text-yellow-700 mt-1">
                  Please start the backend server first: <code className="bg-yellow-100 px-2 py-1 rounded">python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000</code>
                </p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Age *
            </label>
            <input
              type="number"
              min="45"
              max="90"
              required
              value={formData.age}
              onChange={(e) => setFormData({...formData, age: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Enter your age (45-90)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Diet Type *
            </label>
            <select
              value={formData.diet_type}
              onChange={(e) => setFormData({...formData, diet_type: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="balanced">Balanced</option>
              <option value="vegetarian">Vegetarian</option>
              <option value="vegan">Vegan</option>
              <option value="diabetic">Diabetic-Friendly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Allergies (comma-separated)
            </label>
            <input
              type="text"
              value={formData.allergies}
              onChange={(e) => setFormData({...formData, allergies: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g., nuts, dairy, shellfish"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Medical Conditions (comma-separated)
            </label>
            <input
              type="text"
              value={formData.medical_conditions}
              onChange={(e) => setFormData({...formData, medical_conditions: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g., diabetes, hypertension"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Create Profile
          </button>
        </form>
      </Card>
    </div>
  )
}

export default UserProfileForm

