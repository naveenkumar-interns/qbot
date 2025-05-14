import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Cookies from 'js-cookie'
import './Questions.css'

function Questions() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState('')
  const [finished, setFinished] = useState(false)
  const [error, setError] = useState(null)
  const [submitError, setSubmitError] = useState(null)
  const [score, setScore] = useState(null)
  const [showResult, setShowResult] = useState(false)
  const [resultError, setResultError] = useState(null)
  const [resultLoading, setResultLoading] = useState(false)
  const [evaluationEnabled, setEvaluationEnabled] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const username = Cookies.get('username')
    setUser(username)
    if (!username) {
      setError('No user found. Please go back and enter your username.')
      setLoading(false)
      return
    }
    fetch(`http://localhost:8000/api/get_questions/?user=${username}`)
      .then(res => res.json())
      .then(data => {
        if (data.questions && data.questions.length > 0) {
          setQuestions(data.questions)
          setAnswers(Array(data.questions.length).fill(''))
        } else {
          setError('No questions found for this user.')
        }
        setLoading(false)
      })
      .catch(() => {
        setError('Failed to load questions.')
        setLoading(false)
      })
  }, [])

  const handleChange = (idx, value) => {
    const newAnswers = [...answers]
    newAnswers[idx] = value
    setAnswers(newAnswers)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitError(null)
    try {
      const response = await fetch('http://localhost:8000/api/submit_answers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user,
          answers: questions.map((q, idx) => ({
            question: q.question,
            answer: answers[idx]
          }))
        }),
      })
      if (response.ok) {
        setFinished(true)
      } else {
        setSubmitError('Failed to submit answers.')
      }
    } catch {
      setSubmitError('Failed to submit answers.')
    }
  }

  const handleViewResult = async () => {
    setResultError(null)
    setScore(null)
    setShowResult(true)
    setResultLoading(true)
    setEvaluationEnabled(false)
    try {
      setUser(Cookies.get('username'))
      const response = await fetch(`http://localhost:8000/api/evaluate_answers/?user=${user}`)
      const data = await response.json()
      if (response.ok) {
        setScore(data.score)
        setEvaluationEnabled(true)
      } else {
        setResultError(data.error || 'Failed to fetch result.')
      }
    } catch {
      setResultError('Failed to fetch result.')
    }
    setResultLoading(false)
  }

  const handleEvaluation = () => {
    navigate('/evaluation')
  }

  if (loading) return <div className="questions-loading">Loading questions...</div>
  if (error) return <div className="questions-error">{error}</div>
  if (finished) return (
    <div className="result-container">
      <div className="result-card">
        <h2>Test Completed!</h2>
        <p>Thank you for attending the test, <b>{user}</b>.</p>
        {!showResult && (
          <button className="result-btn" onClick={handleViewResult}>View Result</button>
        )}
        {showResult && (
          <div className="score-section">
            {resultLoading && <div className="questions-loading">Evaluating your answers...</div>}
            {resultError && <div className="questions-error">{resultError}</div>}
            {score !== null && !resultLoading && (
              <div className="score-box">
                <span>Your Score</span>
                <h3>{score}%</h3>
              </div>
            )}
            <button
              className="evaluation-btn"
              onClick={handleEvaluation}
              disabled={!evaluationEnabled || resultLoading}
              style={{
                marginTop: '1.5rem',
                background: evaluationEnabled ? '#2563eb' : '#a5b4fc',
                cursor: evaluationEnabled ? 'pointer' : 'not-allowed'
              }}
            >
              Go to Evaluation
            </button>
          </div>
        )}
      </div>
    </div>
  )

  return (
    <div className="questions-container">
      <h2>Answer all questions</h2>
      <form className="questions-form" onSubmit={handleSubmit}>
        {questions.map((q, idx) => (
          <div key={idx} className="question-block">
            <p className="question-text">{q.question}</p>
            <input
              type="text"
              value={answers[idx] || ''}
              onChange={e => handleChange(idx, e.target.value)}
              placeholder="Your answer"
              required
              className="answer-input"
            />
          </div>
        ))}
        <button className="finish-btn" type="submit">Finish Test</button>
        {submitError && <div className="questions-error">{submitError}</div>}
      </form>
    </div>
  )
}

export default Questions