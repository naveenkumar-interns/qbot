import { useState, useEffect } from 'react'
import './App.css'
import { useNavigate } from 'react-router-dom'
import Topic from './pages/Topic'


function App() {
  return (
    <div className="App">
      <h1>Test Agents</h1>
      <Topic />
    </div>
  )
}

export default App

