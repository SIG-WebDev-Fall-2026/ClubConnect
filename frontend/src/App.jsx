import { useEffect } from "react"
import Dashboard from "./components/Dashboard"
import "./App.css"

function App() {
  useEffect(() => {
    fetch("http://localhost:5002/api/health")
      .then((response) => response.json())
      .then((data) => console.log("Backend JSON:", data))
  }, [])

  return <Dashboard />
}

export default App
