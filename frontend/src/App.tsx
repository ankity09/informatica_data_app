import React, { useState } from 'react'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import Chat from './components/Chat'
import TabNavigation from './components/TabNavigation'

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'chat'>('dashboard')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      <Header />
      <main className="container mx-auto px-6 py-8">
        <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <div className="mt-8">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'chat' && <Chat />}
        </div>
      </main>
    </div>
  )
}

export default App 