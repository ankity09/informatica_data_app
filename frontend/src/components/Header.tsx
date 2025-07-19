import React from 'react'
import { Sparkles, Database, MessageSquare } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight">
                  Radius Analytics
                </h1>
                <p className="text-blue-100 text-sm font-medium">
                  AI-Powered Recycling Intelligence
                </p>
              </div>
            </div>
          </div>

          {/* Navigation Features */}
          <div className="hidden md:flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-blue-100">
              <Database className="w-4 h-4" />
              <span className="text-sm font-medium">Databricks Powered</span>
            </div>
            <div className="flex items-center space-x-2 text-blue-100">
              <MessageSquare className="w-4 h-4" />
              <span className="text-sm font-medium">AI Assistant</span>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-blue-100 text-sm font-medium">Live</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 