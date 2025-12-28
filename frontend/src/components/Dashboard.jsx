import React, { useState, useEffect } from 'react'
import { Card } from './ui/Card'
import { TrendingUp, Heart, Calendar, Activity, AlertCircle } from 'lucide-react'
import api from '../utils/api'
import UserProfileForm from './UserProfileForm'
import Chatbot from './Chatbot'

const Dashboard = ({ userProfile, setUserProfile, currentPlan }) => {
  const [stats, setStats] = useState({
    totalPlans: 0,
    adherenceRate: 0,
    avgPlanScore: 0,
    activeStreak: 0
  })

  const [backendError, setBackendError] = useState(false)

  useEffect(() => {
    // Fetch user history
    api.get('/history')
      .then(res => {
        const episodes = res.data.episodes || []
        const adherence = episodes.length > 0 
          ? episodes.reduce((sum, ep) => sum + ep.adherence, 0) / episodes.length
          : 0
        
        setStats({
          totalPlans: episodes.length,
          adherenceRate: Math.round(adherence),
          avgPlanScore: 85,
          activeStreak: episodes.length
        })
        setBackendError(false)
      })
      .catch(err => {
        console.error('Error fetching history:', err)
        setBackendError(true)
        // Set default stats if API fails
        setStats({
          totalPlans: 0,
          adherenceRate: 0,
          avgPlanScore: 0,
          activeStreak: 0
        })
      })
  }, [])

  if (!userProfile) {
    return <UserProfileForm setUserProfile={setUserProfile} />
  }

  return (
    <div className="space-y-6 w-full max-w-full overflow-x-hidden">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's your wellness overview.</p>
      </div>

      {backendError && (
        <Card className="bg-red-50 border-red-200">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div className="flex-1">
              <p className="font-medium text-red-800">Backend API Error</p>
              <p className="text-sm text-red-700 mt-1">
                The backend server is not responding or the wrong backend is running.
              </p>
              <div className="mt-2 space-y-1 text-xs text-red-600">
                <p><strong>To fix:</strong></p>
                <ol className="list-decimal list-inside ml-2 space-y-1">
                  <li>Stop any running backend (Ctrl+C in that terminal)</li>
                  <li>From project root, run: <code className="bg-red-100 px-1 py-0.5 rounded">python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000</code></li>
                  <li>Or use: <code className="bg-red-100 px-1 py-0.5 rounded">.\start_backend.ps1</code></li>
                  <li>Verify at <code className="bg-red-100 px-1 py-0.5 rounded">http://localhost:8000/</code> shows "ElderFit AI API"</li>
                </ol>
              </div>
            </div>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Plans</p>
              <p className="text-3xl font-bold mt-2">{stats.totalPlans}</p>
            </div>
            <Calendar className="w-12 h-12 text-blue-200" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Adherence Rate</p>
              <p className="text-3xl font-bold mt-2">{stats.adherenceRate}%</p>
            </div>
            <TrendingUp className="w-12 h-12 text-green-200" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Avg Plan Score</p>
              <p className="text-3xl font-bold mt-2">{stats.avgPlanScore}</p>
            </div>
            <Heart className="w-12 h-12 text-purple-200" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">Active Streak</p>
              <p className="text-3xl font-bold mt-2">{stats.activeStreak}</p>
            </div>
            <Activity className="w-12 h-12 text-orange-200" />
          </div>
        </Card>
      </div>

      {currentPlan && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Today's Plan</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Breakfast</span>
              <span className="text-gray-600">{currentPlan.plan?.meals?.breakfast?.name}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Lunch</span>
              <span className="text-gray-600">{currentPlan.plan?.meals?.lunch?.name}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Dinner</span>
              <span className="text-gray-600">{currentPlan.plan?.meals?.dinner?.name}</span>
            </div>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4">
            <a href="/check-in" className="p-4 bg-primary-50 rounded-lg border-2 border-primary-200 hover:border-primary-400 transition-colors text-center">
              <p className="font-medium text-primary-700">Daily Check-In</p>
              <p className="text-sm text-primary-600 mt-1">Update your mood and appetite</p>
            </a>
            <a href="/feedback" className="p-4 bg-green-50 rounded-lg border-2 border-green-200 hover:border-green-400 transition-colors text-center">
              <p className="font-medium text-green-700">Submit Feedback</p>
              <p className="text-sm text-green-600 mt-1">Share your experience</p>
            </a>
          </div>
        </Card>
        <Chatbot userProfile={userProfile} language="en" />
      </div>
    </div>
  )
}

export default Dashboard

