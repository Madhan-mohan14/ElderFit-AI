import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  ClipboardCheck, 
  Calendar,
  FileText,
  MessageSquare,
  Brain,
  Activity
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()
  
  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/check-in', icon: ClipboardCheck, label: 'Check-In' },
    { path: '/plan', icon: Calendar, label: 'Today\'s Plan' },
    { path: '/decision-trace', icon: FileText, label: 'Decision Trace' },
    { path: '/feedback', icon: MessageSquare, label: 'Feedback' },
    { path: '/memory', icon: Brain, label: 'Memory Insights' },
  ]

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 pt-16 z-40 overflow-y-auto">
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
      
      <div className="absolute bottom-4 left-4 right-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
        <div className="flex items-start space-x-2">
          <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900">Wellness Coaching Only</p>
            <p className="text-xs text-blue-700 mt-1">Not a medical system</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar

