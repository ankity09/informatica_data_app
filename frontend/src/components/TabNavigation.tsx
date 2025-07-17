import React from 'react'
import { BarChart3, MessageCircle } from 'lucide-react'

interface TabNavigationProps {
  activeTab: 'dashboard' | 'chat'
  setActiveTab: (tab: 'dashboard' | 'chat') => void
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    {
      id: 'dashboard' as const,
      label: 'Dashboard',
      icon: BarChart3,
      description: 'View data insights and analytics'
    },
    {
      id: 'chat' as const,
      label: 'Chat with AI',
      icon: MessageCircle,
      description: 'Ask questions about your data'
    }
  ]

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
      <div className="flex space-x-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab-button flex-1 flex items-center justify-center space-x-2 ${
                isActive ? 'active' : 'inactive'
              }`}
              title={tab.description}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default TabNavigation 