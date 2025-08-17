import React, { useState } from 'react'
import { apiPost } from '../api'
import { useNavigate } from 'react-router-dom'

export default function Register(){
  const [form, setForm] = useState({ name:'', email:'', password:'', wallet_address:'' })
  const [msg, setMsg] = useState(null)
  const nav = useNavigate()

  const onSubmit = async(e)=>{
    e.preventDefault()
    setMsg(null)
    const res = await apiPost('/api/register', form)
    if(res.ok){
      setMsg('Registered ✓ — please login')
      setTimeout(()=>nav('/login'), 900)
    } else {
      setMsg(JSON.stringify(res))
    }
  }

  return (
    <div className="card">
      <h2>Register Farmer</h2>
      <form onSubmit={onSubmit}>
        <label>Name <input value={form.name} onChange={e=>setForm({...form, name:e.target.value})} /></label>
        <label>Email <input type="email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})} /></label>
        <label>Password <input type="password" value={form.password} onChange={e=>setForm({...form, password:e.target.value})} /></label>
        <label>Wallet Address <input value={form.wallet_address} onChange={e=>setForm({...form, wallet_address:e.target.value})} /></label>
        <button type="submit">Create</button>
      </form>
      {msg && <pre>{msg}</pre>}
    </div>
  )
}
