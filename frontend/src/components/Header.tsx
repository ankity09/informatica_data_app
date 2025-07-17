import React from 'react'
import { Leaf, Sparkles } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-radius-600 rounded-lg flex items-center justify-center overflow-hidden">
                <img src="/radius-logo.jpg" alt="Radius Recycling" className="w-full h-full object-cover" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Radius Recycling</h1>
                <p className="text-sm text-gray-500">AI-Powered Data Insights</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Sparkles className="w-4 h-4" />
            <span>Powered by Databricks Mosaic AI</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 