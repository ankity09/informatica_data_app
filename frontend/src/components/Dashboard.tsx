import React from 'react'

const Dashboard: React.FC = () => {

  return (
    <div className="h-screen">
      {/* Databricks Dashboard Embed - Full Width */}
      <div className="h-full flex flex-col">
        <div className="flex items-center justify-between mb-4 p-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
            <p className="text-gray-600 mt-1">Monitor your recycling operations and key metrics</p>
          </div>
          <button 
            className="btn-secondary text-sm"
            onClick={() => window.location.reload()}
          >
            Refresh Dashboard
          </button>
        </div>
        
        <div className="flex-1 bg-white rounded-lg border border-gray-200 overflow-hidden mx-4 mb-4">
          <iframe
            src="https://e2-demo-west.cloud.databricks.com/embed/dashboardsv3/01f05cff69fa1b48b0fb81d09e7dc101?o=2556758628403379"
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