import React from 'react'
import { Card } from './ui/Card'
import { CheckCircle, Brain, Zap, FileText, Lightbulb } from 'lucide-react'

const DecisionTraceViewer = ({ plan }) => {
  if (!plan || !plan.decision_trace) {
    return (
      <Card>
        <p className="text-gray-600">No decision trace available. Please generate a plan first.</p>
      </Card>
    )
  }

  const trace = plan.decision_trace

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Decision Trace</h1>
        <p className="text-gray-600 mt-2">See how your wellness plan was created</p>
      </div>

      <Card>
        <div className="flex items-center space-x-3 mb-6">
          <FileText className="w-6 h-6 text-primary-600" />
          <h2 className="text-xl font-semibold">Plan Explanation</h2>
        </div>
        <p className="text-gray-700 leading-relaxed">{trace.explanation}</p>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <div className="flex items-center space-x-3 mb-4">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold">Triggered Rules</h3>
          </div>
          <ul className="space-y-2">
            {trace.triggered_rules && trace.triggered_rules.map((rule, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-green-500 mt-1">•</span>
                <span className="text-gray-700">{rule}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <div className="flex items-center space-x-3 mb-4">
            <Zap className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold">APIs Called</h3>
          </div>
          <ul className="space-y-2">
            {trace.apis_called && trace.apis_called.map((api, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-blue-500 mt-1">•</span>
                <span className="text-gray-700">{api}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <div className="flex items-center space-x-3 mb-4">
            <Brain className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold">Retrieved Memories</h3>
          </div>
          <p className="text-gray-700">
            {trace.retrieved_memories && trace.retrieved_memories.length > 0
              ? `Retrieved ${trace.retrieved_memories.length} similar past episodes to inform this plan`
              : 'No similar memories found (this may be your first plan)'}
          </p>
          {trace.retrieved_memories && trace.retrieved_memories.length > 0 && (
            <div className="mt-4 space-y-2">
              {trace.retrieved_memories.map((mem, idx) => (
                <div key={idx} className="p-3 bg-purple-50 rounded-lg">
                  <p className="text-sm font-medium text-purple-900">Episode #{mem}</p>
                  <p className="text-xs text-purple-700">Used to inform current plan</p>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <div className="flex items-center space-x-3 mb-4">
            <Lightbulb className="w-5 h-5 text-yellow-600" />
            <h3 className="text-lg font-semibold">Mood Interpretation</h3>
          </div>
          <p className="text-gray-700">{trace.mood_interpretation}</p>
        </Card>
      </div>

      <Card className="bg-gradient-to-br from-primary-50 to-primary-100">
        <h3 className="text-lg font-semibold text-primary-900 mb-2">Plan Score</h3>
        <div className="flex items-center space-x-4">
          <div className="text-4xl font-bold text-primary-700">
            {plan.plan ? Math.round(plan.plan.plan_score * 100) : 0}
          </div>
          <div className="flex-1">
            <div className="w-full bg-primary-200 rounded-full h-4">
              <div
                className="bg-primary-600 h-4 rounded-full transition-all"
                style={{
                  width: `${plan.plan ? plan.plan.plan_score * 100 : 0}%`
                }}
              />
            </div>
            <p className="text-sm text-primary-700 mt-2">
              This score considers mood fit, nutrition, simplicity, and your preferences
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default DecisionTraceViewer

