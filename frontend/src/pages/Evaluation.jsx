import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Cookies from 'js-cookie'
import './evaluation.css'

function Evaluation() {
  const [evaluations, setEvaluations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const user = Cookies.get('username')
  const navigate = useNavigate()

  useEffect(() => {
    async function fetchEvaluations() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch('http://localhost:8000/api/get_evaluations/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ user }),
        })
        const data = await response.json()
        if (response.ok) {
          setEvaluations(data.test || [])
        } else {
          setError(data.error || 'Failed to fetch evaluation results.')
        }
      } catch {
        setError('Failed to fetch evaluation results.')
      }
      setLoading(false)
    }
    fetchEvaluations()
  }, [user])

  if (loading) return <div className="evaluation-loading">Loading evaluation results...</div>
  if (error) return <div className="evaluation-error">{error}</div>

  return (
    <div className="evaluation-container">
      <h1>Evaluation Results</h1>
      <div className="evaluation-list">
        {evaluations.map((item, idx) => (
          <div className="evaluation-card" key={idx}>
            <div className="evaluation-question">
              <b>Q{idx + 1}:</b> {item.question}
            </div>
            <div className="evaluation-answer">
              <span className="label">Correct Answer:</span> {item.answer}
            </div>
            <div className="evaluation-user-answer">
              <span className="label">Your Answer:</span> {item.user_answer}
            </div>
            <div className="evaluation-score">
              <span className="label">Score:</span> <b>{item.score}</b>
            </div>
            <div className="evaluation-reason">
              <span className="label">Reason:</span> {item.reason}
            </div>
            <div className="evaluation-suggestion">
              <span className="label">Suggestion:</span> {item.suggestion}
            </div>
          </div>
        ))}
      </div>
      <button className="back-btn" onClick={() => navigate('/')}>Back to Home</button>
    </div>
  )
}

export default Evaluation