import React from 'react'
import Detector from './components/Detector'
import './App.css'

function App(): JSX.Element {
  return (
    <div className="container">
      <h1>🔍 Lost & Found Detector</h1>
      <p className="subtitle">Capture and identify lost items using AI</p>
      <Detector />
    </div>
  )
}

export default App

