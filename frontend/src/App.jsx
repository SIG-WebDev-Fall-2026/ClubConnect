import Dashboard from "./pages/Dashboard"
import { Route,Routes } from 'react-router-dom'
import Navbar from "./components/Navbar"
import "./App.css"
import Login from "./pages/Login.jsx"
import Register from "./pages/Register.jsx"
import UnauthenticatedRoute from './UnauthenticatedRoute'
import NotFound from "./NotFound"
import ProtectedRoute from './ProtectedRoute.jsx'



function App() {
  return (
    <>
      <Routes>
        <Route element={<UnauthenticatedRoute/>}>
          <Route path='log-in' element={<Login/>}/>
          <Route path='register' element={<Register/>}/>
        </Route>
        <Route element={<ProtectedRoute/>}>
          <Route index element={<Dashboard />}/>
        </Route>
        <Route path='*' element={<NotFound/>}/>
      </Routes>
      {/* <Navbar /> */}  
    </>
  )
}

export default App