'use client'

interface ResultInsightsProps {
  summary?: string
  insights?: string
  keyMetrics?: Record<string, any>
}

export default function ResultInsights({ summary, insights, keyMetrics }: ResultInsightsProps) {
  if (!summary && !insights && !keyMetrics) {
    return null
  }

  return (
    <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
      <h3 className="font-semibold mb-3 text-blue-900">💡 Resumo e Insights</h3>
      
      {summary && (
        <div className="mb-3">
          <p className="text-gray-800">{summary}</p>
        </div>
      )}
      
      {insights && (
        <div className="mb-3">
          <h4 className="font-semibold mb-1 text-blue-800">Análise:</h4>
          <p className="text-gray-700">{insights}</p>
        </div>
      )}
      
      {keyMetrics && Object.keys(keyMetrics).length > 0 && (
        <div>
          <h4 className="font-semibold mb-2 text-blue-800">Métricas Principais:</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(keyMetrics).map(([key, value]) => (
              <div key={key} className="bg-white p-2 rounded">
                <span className="font-medium text-gray-700">{key}:</span>{' '}
                <span className="text-gray-900">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
