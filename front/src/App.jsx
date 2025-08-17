import React, { useState } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import Register from "./pages/Register";
import VerifyOTP from "./pages/VerifyOTP";
import AddLand from "./pages/AddLand";
import Login from "./pages/Login";
import Claim from "./pages/Claim";
import Payout from "./pages/Payout";

export default function App(){
  const [session, setSession] = useState(null)
  const nav = useNavigate()
  const logout = ()=>{ setSession(null); nav('/login') }
  return (
    <div className="container">
      <header className="header">
        <h1>Hack Beyond Limits</h1>
        <nav>
          <Link to="/register">Register</Link>
          <Link to="/login">Login</Link>
          <Link to="/add-land">Add Land</Link>
          <Link to="/claim">Claim</Link>
          <button onClick={logout}>Logout</button>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Login onLogin={setSession} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify" element={<VerifyOTP />} />
          <Route path="/add-land" element={<AddLand />} />
          <Route path="/login" element={<Login onLogin={setSession} />} />
          <Route path="/claim" element={<Claim session={session} />} />
          <Route path="/payout" element={<Payout />} />
        </Routes>
      </main>
    </div>
  )
}
