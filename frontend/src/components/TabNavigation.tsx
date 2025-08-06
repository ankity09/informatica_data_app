import React from 'react'
import { BarChart3, MessageSquare, Sparkles } from 'lucide-react'

interface TabNavigationProps {
  activeTab: 'dashboard' | 'chat'
  setActiveTab: (tab: 'dashboard' | 'chat') => void
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    {
      id: 'dashboard' as const,
      label: 'Analytics Dashboard',
      icon: BarChart3,
      description: 'View your data insights'
    },
    {
      id: 'chat' as const,
      label: 'AI Assistant',
      icon: MessageSquare,
      description: 'Chat with your data intelligence'
    }
  ]

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-2 shadow-lg border border-white/20">
      <div className="flex space-x-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex-1 flex items-center justify-center space-x-3 px-6 py-4 rounded-xl
                transition-all duration-300 ease-out transform
                ${isActive 
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg scale-105' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
                }
              `}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
              <div className="text-left">
                <div className={`font-semibold text-sm ${isActive ? 'text-white' : 'text-gray-900'}`}>
                  {tab.label}
                </div>
                <div className={`text-xs ${isActive ? 'text-blue-100' : 'text-gray-500'}`}>
                  {tab.description}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default TabNavigation 