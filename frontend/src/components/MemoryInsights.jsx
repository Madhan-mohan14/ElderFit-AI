import React, { useState, useEffect } from 'react'
import { Card } from './ui/Card'
import { Brain, Heart, TrendingUp, Clock } from 'lucide-react'
import api from '../utils/api'

const MemoryInsights = () => {
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInsights()
  }, [])

  const fetchInsights = async () => {
    try {
      const response = await api.get('/memory-insights')
      setInsights(response.data)
    } catch (error) {
      console.error('Error fetching insights:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <p className="text-gray-600">Loading memory insights...</p>
      </Card>
    )
  }

  if (!insights) {
    return (
      <Card>
        <p className="text-gray-600">No memory insights available yet.</p>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Brain className="w-8 h-8 mr-3 text-primary-600" />
          Memory Insights
        </h1>
        <p className="text-gray-600 mt-2">Your personalized preferences learned over time</p>
      </div>

      <Card>
        <div className="flex items-center space-x-3 mb-6">
          <Heart className="w-6 h-6 text-red-500" />
          <h2 className="text-xl font-semibold">Liked Foods</h2>
        </div>
        {insights.preferences?.liked_foods && insights.preferences.liked_foods.length > 0 ? (
          <div className="flex flex-wrap gap-3">
            {insights.preferences.liked_foods.map((food, idx) => (
              <span
                key={idx}
                className="px-4 py-2 bg-green-50 text-green-700 rounded-full text-sm font-medium border border-green-200"
              >
                {food}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No preferred foods recorded yet. Start rating meals to build your preferences!</p>
        )}
      </Card>

      <Card>
        <div className="flex items-center space-x-3 mb-6">
          <TrendingUp className="w-6 h-6 text-blue-500" />
          <h2 className="text-xl font-semibold">Liked Exercises</h2>
        </div>
        {insights.preferences?.liked_videos && insights.preferences.liked_videos.length > 0 ? (
          <div className="space-y-2">
            {insights.preferences.liked_videos.map((videoId, idx) => (
              <div
                key={idx}
                className="p-3 bg-blue-50 rounded-lg border border-blue-200"
              >
                <p className="text-sm text-blue-700">Video #{videoId}</p>
                <p className="text-xs text-blue-600">Recommended based on your preferences</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No preferred exercises recorded yet. Start rating videos to build your preferences!</p>
        )}
      </Card>

      {insights.similar_episodes && insights.similar_episodes.length > 0 && (
        <Card>
          <div className="flex items-center space-x-3 mb-6">
            <Clock className="w-6 h-6 text-purple-500" />
            <h2 className="text-xl font-semibold">Similar Past Episodes</h2>
          </div>
          <div className="space-y-4">
            {insights.similar_episodes.map((episode, idx) => (
              <div
                key={idx}
                className="p-4 bg-purple-50 rounded-lg border border-purple-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium text-purple-900">Episode #{episode.id || idx + 1}</p>
                  <span className="text-sm text-purple-700">{episode.date || 'Recent'}</span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-purple-600">Mood</p>
                    <p className="font-medium text-purple-900 capitalize">{episode.mood || 'neutral'}</p>
                  </div>
                  <div>
                    <p className="text-purple-600">Appetite</p>
                    <p className="font-medium text-purple-900 capitalize">{episode.appetite || 'normal'}</p>
                  </div>
                  <div>
                    <p className="text-purple-600">Adherence</p>
                    <p className="font-medium text-purple-900">{episode.adherence || 0}%</p>
                  </div>
                </div>
                {episode.liked_foods && episode.liked_foods.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-purple-200">
                    <p className="text-xs text-purple-600 mb-1">Liked foods:</p>
                    <div className="flex flex-wrap gap-2">
                      {episode.liked_foods.slice(0, 3).map((food, foodIdx) => (
                        <span
                          key={foodIdx}
                          className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs"
                        >
                          {food}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card className="bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200">
        <h3 className="text-lg font-semibold text-primary-900 mb-2">How Memory Works</h3>
        <p className="text-sm text-primary-700 leading-relaxed">
          ElderFit AI uses associative memory to learn from your past wellness experiences. 
          When you rate meals and exercises, the system remembers your preferences and uses 
          similar past episodes to create better plans. This helps personalize your wellness 
          journey over time.
        </p>
      </Card>
    </div>
  )
}

export default MemoryInsights

