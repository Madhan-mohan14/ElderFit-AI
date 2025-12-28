import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import CheckInPanel from './components/CheckInPanel'
import PlanExecution from './components/PlanExecution'
import DecisionTraceViewer from './components/DecisionTraceViewer'
import FeedbackPanel from './components/FeedbackPanel'
import MemoryInsights from './components/MemoryInsights'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'

function App() {
  // Load userProfile from localStorage on mount
  const [userProfile, setUserProfile] = useState(() => {
    const saved = localStorage.getItem('userProfile')
    return saved ? JSON.parse(saved) : null
  })
  const [currentPlan, setCurrentPlan] = useState(() => {
    const saved = localStorage.getItem('currentPlan')
    return saved ? JSON.parse(saved) : null
  })
  const [language, setLanguage] = useState('en')

  // Update localStorage when userProfile changes
  useEffect(() => {
    if (userProfile) {
      localStorage.setItem('userProfile', JSON.stringify(userProfile))
    } else {
      localStorage.removeItem('userProfile')
    }
  }, [userProfile])

  // Update localStorage when currentPlan changes
  useEffect(() => {
    if (currentPlan) {
      console.log('Saving plan to localStorage:', currentPlan)
      try {
        localStorage.setItem('currentPlan', JSON.stringify(currentPlan))
      } catch (e) {
        console.error('Error saving plan to localStorage:', e)
      }
    } else {
      localStorage.removeItem('currentPlan')
    }
  }, [currentPlan])
  
  // Debug: Log when currentPlan changes
  useEffect(() => {
    console.log('currentPlan state changed:', currentPlan)
  }, [currentPlan])

  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <div className="min-h-screen bg-gray-50 w-full overflow-x-hidden">
        <Header language={language} setLanguage={setLanguage} />
        <div className="flex w-full">
          <Sidebar />
          <main className="flex-1 ml-64 pt-20 px-8 pb-8 w-full max-w-full overflow-x-hidden">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route 
                path="/dashboard" 
                element={
                  <Dashboard 
                    userProfile={userProfile}
                    setUserProfile={setUserProfile}
                    currentPlan={currentPlan}
                  />
                } 
              />
              <Route 
                path="/check-in" 
                element={
                  <CheckInPanel 
                    userProfile={userProfile}
                    setCurrentPlan={setCurrentPlan}
                    language={language}
                  />
                } 
              />
              <Route 
                path="/plan" 
                element={
                  <PlanExecution 
                    plan={currentPlan}
                    language={language}
                  />
                } 
              />
              <Route 
                path="/decision-trace" 
                element={
                  <DecisionTraceViewer 
                    plan={currentPlan}
                  />
                } 
              />
              <Route 
                path="/feedback" 
                element={
                  <FeedbackPanel 
                    plan={currentPlan}
                  />
                } 
              />
              <Route 
                path="/memory" 
                element={<MemoryInsights />} 
              />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App

