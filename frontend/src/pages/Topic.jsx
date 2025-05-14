import { useState } from 'react'
import './Topic.css'

function Topic() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResponse(null)
    try {
      const res = await fetch('http://localhost:5000/api/topic', { // Change URL as needed
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      })
      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setResponse({ error: 'Failed to send topic' })
    }
    setLoading(false)
  }

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Submit'}
        </button>
      </form>
      {response && (
        <div>
          {response.error ? (
            <span style={{ color: 'red' }}>{response.error}</span>
          ) : (
            <pre>{JSON.stringify(response, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  )
}

export default Topic