import React, { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, Users, Package } from 'lucide-react'
import { Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface DashboardData {
  collections: Array<{ month: string; value: number }>
  revenue: Array<{ month: string; value: number }>
  metrics: {
    total_collections: string
    active_customers: string
    monthly_revenue: string
    efficiency_score: string
  }
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/dashboard-data')
        const dashboardData = await response.json()
        setData(dashboardData)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard data...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500">Failed to load dashboard data</div>
      </div>
    )
  }

  const collectionsChartData = {
    labels: data.collections.map(item => item.month),
    datasets: [
      {
        label: 'Collections',
        data: data.collections.map(item => item.value),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.1,
      },
    ],
  }

  const revenueChartData = {
    labels: data.revenue.map(item => item.month),
    datasets: [
      {
        label: 'Revenue ($)',
        data: data.revenue.map(item => item.value),
        backgroundColor: 'rgba(14, 165, 233, 0.8)',
        borderColor: 'rgb(14, 165, 233)',
        borderWidth: 1,
      },
    ],
  }

  const stats = [
    {
      title: 'Total Collections',
      value: data.metrics.total_collections,
      change: '+12.5%',
      changeType: 'positive' as const,
      icon: Package,
      color: 'bg-blue-500'
    },
    {
      title: 'Active Customers',
      value: data.metrics.active_customers,
      change: '+8.2%',
      changeType: 'positive' as const,
      icon: Users,
      color: 'bg-green-500'
    },
    {
      title: 'Monthly Revenue',
      value: data.metrics.monthly_revenue,
      change: '+15.3%',
      changeType: 'positive' as const,
      icon: TrendingUp,
      color: 'bg-purple-500'
    },
    {
      title: 'Efficiency Score',
      value: data.metrics.efficiency_score,
      change: '+2.1%',
      changeType: 'positive' as const,
      icon: BarChart3,
      color: 'bg-orange-500'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600 mt-1">Monitor your recycling operations and key metrics</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <p className={`text-sm mt-1 ${
                    stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change} from last month
                  </p>
                </div>
                <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Collections Trend</h3>
          <Line 
            data={collectionsChartData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'top' as const,
                },
                title: {
                  display: false,
                },
              },
            }}
          />
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h3>
          <Bar 
            data={revenueChartData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'top' as const,
                },
                title: {
                  display: false,
                },
              },
            }}
          />
        </div>
      </div>

      {/* Dashboard Embed Area */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Analytics Dashboard</h3>
          <button className="btn-secondary text-sm">
            Refresh Data
          </button>
        </div>
        
        <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">Dashboard Embed</h4>
          <p className="text-gray-600 mb-4">
            Your embedded dashboard will appear here. You can embed Databricks dashboards, 
            Tableau, Power BI, or any other analytics platform.
          </p>
          <div className="space-y-2 text-sm text-gray-500">
            <p>• Embed URL: <code className="bg-gray-200 px-2 py-1 rounded">https://your-dashboard-url.com</code></p>
            <p>• Recommended size: 1200x800 pixels</p>
            <p>• Supports iframe embedding</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn-primary">
            Generate Report
          </button>
          <button className="btn-secondary">
            Export Data
          </button>
          <button className="btn-secondary">
            Schedule Alert
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 