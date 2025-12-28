import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = '/api'

function App() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [documents, setDocuments] = useState([])
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [activeTab, setActiveTab] = useState('query')

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE}/documents`)
      setDocuments(response.data.documents)
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    }
  }

  const handleQuery = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setAnswer(null)

    try {
      const response = await axios.post(`${API_BASE}/query`, { query })
      setAnswer(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get answer')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!uploadFile) return

    const formData = new FormData()
    formData.append('file', uploadFile)

    setUploadStatus('uploading')

    try {
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadStatus('success')
      setUploadFile(null)
      setTimeout(() => {
        fetchDocuments()
        setUploadStatus(null)
      }, 2000)
    } catch (err) {
      setUploadStatus('error')
      console.error('Upload failed:', err)
    }
  }

  const handleFeedback = async (isCorrect) => {
    try {
      await axios.post(`${API_BASE}/feedback`, {
        query,
        answer: answer.answer,
        is_correct: isCorrect
      })
      alert('Thank you for your feedback!')
    } catch (err) {
      console.error('Feedback failed:', err)
    }
  }

  const handleDeleteDocument = async (documentId, filename) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return
    }

    try {
      await axios.delete(`${API_BASE}/documents/${documentId}`)
      alert('Document deleted successfully!')
      fetchDocuments()
    } catch (err) {
      console.error('Delete failed:', err)
      alert('Failed to delete document. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-indigo-600">UniPolicyQA</h1>
          <p className="text-gray-600 mt-1">AI-Powered University Policy Assistant</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('query')}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              activeTab === 'query'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Ask Question
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              activeTab === 'upload'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Upload Documents
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              activeTab === 'documents'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Documents ({documents.length})
          </button>
        </div>

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <form onSubmit={handleQuery}>
                <label className="block text-gray-700 font-semibold mb-2">
                  Ask a question about university policies:
                </label>
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., What is the attendance policy?"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  rows="4"
                />
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                >
                  {loading ? 'Searching...' : 'Get Answer'}
                </button>
              </form>

              {error && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700">{error}</p>
                </div>
              )}

              {answer && (
                <div className="mt-6 space-y-4">
                  {/* Summary (if available) */}
                  {answer.summary && (
                    <div className="p-6 bg-gradient-to-r from-indigo-100 to-purple-100 border-2 border-indigo-300 rounded-lg shadow-md">
                      <div className="flex items-start">
                        <span className="text-2xl mr-3">💡</span>
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-indigo-900 mb-2">Quick Summary</h3>
                          <p className="text-gray-900 text-base leading-relaxed">{answer.summary}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Detailed Answer */}
                  <div className="p-6 bg-indigo-50 border border-indigo-200 rounded-lg">
                    <h3 className="text-lg font-semibold text-indigo-900 mb-2">
                      {answer.detailed_answer ? 'Detailed Information:' : 'Answer:'}
                    </h3>
                    <p className="text-gray-800 whitespace-pre-wrap">
                      {answer.detailed_answer || answer.answer}
                    </p>

                    {/* Confidence */}
                    <div className="mt-4 flex items-center">
                      <span className="text-sm font-medium text-gray-600 mr-2">Confidence:</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                        <div
                          className={`h-2 rounded-full ${
                            answer.confidence_score > 0.7 ? 'bg-green-500' :
                            answer.confidence_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${answer.confidence_score * 100}%` }}
                        />
                      </div>
                      <span className="ml-2 text-sm font-semibold">{(answer.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  {/* Warnings */}
                  {answer.warnings && answer.warnings.length > 0 && (
                    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Warnings:</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {answer.warnings.map((warning, idx) => (
                          <li key={idx} className="text-yellow-700 text-sm">{warning}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Citations */}
                  {answer.citations && answer.citations.length > 0 && (
                    <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                      <h4 className="font-semibold text-gray-800 mb-2">📚 Citations:</h4>
                      <div className="space-y-2">
                        {answer.citations.slice(0, 3).map((citation, idx) => (
                          <div key={idx} className="text-sm">
                            <p className="font-medium text-gray-700">
                              {citation.filename} - Page {citation.page_number}
                            </p>
                            <p className="text-gray-600 text-xs mt-1 italic">
                              "{citation.text_snippet}"
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {answer.recommendations && answer.recommendations.length > 0 && (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h4 className="font-semibold text-blue-800 mb-2">💡 Recommendations:</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {answer.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-blue-700 text-sm">{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Follow-up Questions */}
                  {answer.followup_questions && answer.followup_questions.length > 0 && (
                    <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                      <h4 className="font-semibold text-purple-800 mb-2">Related Questions:</h4>
                      <div className="space-y-2">
                        {answer.followup_questions.map((q, idx) => (
                          <button
                            key={idx}
                            onClick={() => setQuery(q)}
                            className="block text-left text-purple-700 text-sm hover:text-purple-900 hover:underline"
                          >
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Feedback */}
                  <div className="flex space-x-4 pt-2">
                    <button
                      onClick={() => handleFeedback(true)}
                      className="flex-1 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition"
                    >
                      👍 Helpful
                    </button>
                    <button
                      onClick={() => handleFeedback(false)}
                      className="flex-1 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
                    >
                      👎 Not Helpful
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Policy Document</h2>
              <form onSubmit={handleUpload}>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc"
                    onChange={(e) => setUploadFile(e.target.files[0])}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer text-indigo-600 hover:text-indigo-700"
                  >
                    <div className="text-4xl mb-2">📄</div>
                    <p className="font-semibold">Click to select a file</p>
                    <p className="text-sm text-gray-500 mt-1">PDF or DOCX (max 50MB)</p>
                  </label>
                  {uploadFile && (
                    <p className="mt-4 text-sm text-gray-700">Selected: {uploadFile.name}</p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={!uploadFile || uploadStatus === 'uploading'}
                  className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                >
                  {uploadStatus === 'uploading' ? 'Uploading...' : 'Upload Document'}
                </button>
              </form>

              {uploadStatus === 'success' && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-700">✓ Document uploaded successfully!</p>
                </div>
              )}

              {uploadStatus === 'error' && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700">✗ Upload failed. Please try again.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-800">Uploaded Documents</h2>
                {documents.length > 0 && (
                  <span className="text-sm text-gray-600">{documents.length} document{documents.length !== 1 ? 's' : ''}</span>
                )}
              </div>
              {documents.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📚</div>
                  <p className="text-gray-500 text-lg">No documents uploaded yet.</p>
                  <p className="text-gray-400 text-sm mt-2">Upload a document to get started!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div key={doc.document_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition group">
                      <div className="flex items-center flex-1">
                        <div className="text-3xl mr-4">📄</div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-800">{doc.filename}</p>
                          <p className="text-sm text-gray-500">
                            {doc.chunk_count} chunks • {doc.document_type.toUpperCase()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteDocument(doc.document_id, doc.filename)}
                        className="ml-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition opacity-0 group-hover:opacity-100 flex items-center"
                        title="Delete document"
                      >
                        <span className="mr-1">🗑️</span>
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-gray-600 text-sm">
          <p>UniPolicyQA - Powered by Google Gemini & Hugging Face</p>
          <p className="mt-1">Always verify critical information with official university sources</p>
        </div>
      </footer>
    </div>
  )
}

export default App
