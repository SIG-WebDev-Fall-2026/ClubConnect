import { useEffect } from "react"
import Dashboard from "./pages/Dashboard"
import Navbar from "./components/Navbar"
import "./App.css"

function App() {
  useEffect(() => {
    fetch("http://localhost:5002/api/health")
      .then((response) => response.json())
      .then((data) => console.log("Backend JSON:", data))
  }, [])

  return (
    <>
      <Navbar />
      <Dashboard />
    </>
  )
}

export default App
