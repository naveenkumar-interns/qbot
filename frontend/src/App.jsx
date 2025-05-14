import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import Topic from './pages/Topic'
import Questions from './pages/Questions'
import Evaluation from './pages/Evaluation'

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <h1>Test Agents</h1>
        <Routes>
          <Route path="/" element={<Topic />} />
          <Route path="/questions" element={<Questions />} />
          <Route path="/evaluation" element={<Evaluation />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App