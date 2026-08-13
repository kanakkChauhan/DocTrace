import { useEffect, useState } from 'react'

function App() {
  const [health, setHealth] = useState<string>('Checking system health...')
  const [isOnline, setIsOnline] = useState<boolean>(false)

  useEffect(() => {
    fetch('/api/v1/system/health')
      .then(res => {
        if (!res.ok) throw new Error('Network response was not ok')
        return res.json()
      })
      .then(data => {
        setHealth(`System Status: ${data.status.toUpperCase()} (${data.environment})`)
        setIsOnline(true)
      })
      .catch(() => {
        setHealth('System Status: OFFLINE - Backend not reachable')
        setIsOnline(false)
      })
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white shadow-md rounded-lg p-8 text-center border border-gray-200">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">DocTrace</h1>
        <p className="text-gray-500 mb-6">Documentation Verification Engine</p>
        
        <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
          isOnline ? 'bg-blue-50 text-blue-700' : 'bg-red-50 text-red-700'
        }`}>
          <span className={`w-2 h-2 rounded-full mr-2 ${
            isOnline ? 'bg-blue-600 animate-pulse' : 'bg-red-600'
          }`}></span>
          {health}
        </div>
      </div>
    </div>
  )
}

export default App