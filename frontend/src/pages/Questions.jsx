import { useEffect, useState } from 'react'
import Cookies from 'js-cookie'

function Questions() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState('')
  const [finished, setFinished] = useState(false)
  const [error, setError] = useState(null)
  const [submitError, setSubmitError] = useState(null)

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

  if (loading) return <div>Loading questions...</div>
  if (error) return <div style={{ color: 'red' }}>{error}</div>
  if (finished) return (
    <div>
      <h2>Test Completed!</h2>
      <p>Thank you for attending the test, {user}.</p>
    </div>
  )

  return (
    <div className="questions-container">
      <h2>Answer all questions</h2>
      <form onSubmit={handleSubmit}>
        {questions.map((q, idx) => (
          <div key={idx} style={{ marginBottom: '1rem' }}>
            <p>{q.question}</p>
            <input
              type="text"
              value={answers[idx] || ''}
              onChange={e => handleChange(idx, e.target.value)}
              placeholder="Your answer"
              required
            />
          </div>
        ))}
        <button type="submit">Finish Test</button>
        {submitError && <div style={{ color: 'red' }}>{submitError}</div>}
      </form>
    </div>
  )
}

export default Questions