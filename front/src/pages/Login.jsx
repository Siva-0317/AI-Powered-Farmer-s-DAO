import React, { useState } from 'react'
import { apiPost } from '../api'
import { useNavigate } from 'react-router-dom'

export default function Login({ onLogin }){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState(null)
  const nav = useNavigate()

  const onSubmit = async(e)=>{
    e.preventDefault()
    setErr(null)
    const res = await apiPost('/api/login', { email, password })
    if(!res.ok){ setErr(res.error || 'login failed'); return }
    onLogin(res.data)
    nav('/claim')
  }

  return (
    <div className="card">
      <h2>Login</h2>
      <form onSubmit={onSubmit}>
        <label>Email <input type="email" value={email} onChange={e=>setEmail(e.target.value)} /></label>
        <label>Password <input type="password" value={password} onChange={e=>setPassword(e.target.value)} /></label>
        <button type="submit">Login</button>
      </form>
      {err && <p style={{color:'#ff9aa2'}}>{err}</p>}
    </div>
  )
}
