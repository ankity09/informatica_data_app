import React from 'react'
import { RefreshCw, Maximize2 } from 'lucide-react'

const Dashboard: React.FC = () => {
  return (
    <div className="h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Dashboard Container */}
      <div className="h-full flex flex-col p-6">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-6">
          <div className="space-y-1">
            <h2 className="text-3xl font-bold text-gray-900 tracking-tight">
              Analytics Dashboard
            </h2>
            <p className="text-gray-600 text-lg">
              Real-time insights into your recycling operations
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button 
              className="flex items-center space-x-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-xl border border-white/20 text-gray-700 hover:bg-white transition-all duration-200 shadow-sm"
              onClick={() => window.location.reload()}
            >
              <RefreshCw className="w-4 h-4" />
              <span className="font-medium">Refresh</span>
            </button>
            <button 
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
              onClick={() => window.open('https://e2-demo-field-eng.cloud.databricks.com/embed/dashboardsv3/01f01e4558791c2a8806ade6f298da2c?o=1444828305810485', '_blank')}
            >
              <Maximize2 className="w-4 h-4" />
              <span className="font-medium">Fullscreen</span>
            </button>
          </div>
        </div>
        
        {/* Dashboard Frame */}
        <div className="flex-1 bg-white/90 backdrop-blur-sm rounded-2xl border border-white/20 shadow-xl overflow-hidden">
          <iframe
            src="https://e2-demo-field-eng.cloud.databricks.com/embed/dashboardsv3/01f01e4558791c2a8806ade6f298da2c?o=1444828305810485"
            width="100%"
            height="100%"
            frameBorder="0"
            title="Databricks Analytics Dashboard"
            className="w-full h-full"
            style={{ minHeight: '600px' }}
          />
        </div>
      </div>
    </div>
  )
}

export default Dashboard 