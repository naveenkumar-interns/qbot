import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Cookies from 'js-cookie'
import './Topic.css'

function Topic() {
  const [topic, setTopic] = useState('')
  const [user, setUser] = useState('')
  const [mail, setMail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      // Store username in cookies
      Cookies.set('username', user, { expires: 7 }) // expires in 7 days

      const res = await fetch('http://localhost:8000/api/generate_questions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, user, mail }),
      })
      if (res.ok) {
        navigate('/questions')
      } else {
        setError('Failed to generate questions')
      }
    } catch (err) {
      setError('Failed to send topic')
    }
    setLoading(false)
  }

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={user}
          onChange={(e) => setUser(e.target.value)}
          placeholder="Enter your username"
          required
        />
        <input
          type="text"
          value={mail}
          onChange={(e) => setMail(e.target.value)}
          placeholder="Enter your Mail ID"
          required
        />
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
      {error && (
        <span style={{ color: 'red' }}>{error}</span>
      )}
    </div>
  )
}

export default Topic