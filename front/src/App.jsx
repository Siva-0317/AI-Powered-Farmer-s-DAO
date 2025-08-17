import React, { useState } from 'react'
import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import Register from './pages/Register'
import Login from './pages/Login'
import Claim from './pages/Claim'

export default function App(){
  const [session, setSession] = useState(null)
  const nav = useNavigate()

  const logout = () => { setSession(null); nav('/login') }

  return (
    <div className="container">
      <header className="header">
        <h1>Hack Beyond Limits — Insurance</h1>
        <nav>
          <Link to="/register">Register</Link>
          <Link to="/login">Login</Link>
          {session && <Link to="/claim">Claim</Link>}
          {session && <button onClick={logout}>Logout</button>}
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Login onLogin={setSession} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login onLogin={setSession} />} />
          <Route path="/claim" element={<Claim session={session} />} />
        </Routes>
      </main>
    </div>
  )
}
