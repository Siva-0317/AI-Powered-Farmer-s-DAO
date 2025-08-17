// front/src/pages/FarmerForm.jsx
import React, { useState } from 'react'
import { apiPost } from '../api'
import WalletConnect from '../WalletConnect'

export default function FarmerForm(){
  const [form, setForm] = useState({ name:'', mobile:'', aadhaar:'', wallet_address:'' })
  const [govFile, setGovFile] = useState(null)
  const [selfieFile, setSelfieFile] = useState(null)
  const [otpInfo, setOtpInfo] = useState(null)
  const [status, setStatus] = useState(null)

  const onFile = (e, setter) => setter(e.target.files[0])

  const submit = async (e) => {
    e.preventDefault()
    const fd = new FormData()
    fd.append('name', form.name)
    fd.append('mobile', form.mobile)
    fd.append('aadhaar', form.aadhaar)
    fd.append('wallet_address', form.wallet_address)
    if (govFile) fd.append('gov_id_file', govFile)
    if (selfieFile) fd.append('selfie_file', selfieFile)
    setStatus('Registering...')
    const res = await apiPost('/api/register', fd, true)
    if (!res.ok) { setStatus('Error: ' + (res.error || 'unknown')); return }
    setOtpInfo(res.data)
    setStatus('Registered. OTP (prototype): ' + res.data.otp + '. Use this to verify on next step.')
  }

  const onWalletConnected = ({address}) => {
    setForm({...form, wallet_address: address})
  }

  return (
    <div className="card">
      <h2>Farmer Registration</h2>
      <WalletConnect onConnected={onWalletConnected} />
      <form onSubmit={submit}>
        <label>Name <input value={form.name} onChange={e=>setForm({...form, name:e.target.value})} /></label>
        <label>Mobile <input value={form.mobile} onChange={e=>setForm({...form, mobile:e.target.value})} /></label>
        <label>Aadhaar <input value={form.aadhaar} onChange={e=>setForm({...form, aadhaar:e.target.value})} /></label>
        <label>Wallet Address <input value={form.wallet_address} onChange={e=>setForm({...form, wallet_address:e.target.value})} /></label>

        <label>Govt ID (photo) <input type="file" accept="image/*" onChange={e=>onFile(e, setGovFile)} /></label>
        <label>Selfie (photo) <input type="file" accept="image/*" onChange={e=>onFile(e, setSelfieFile)} /></label>

        <button type="submit">Register & Upload</button>
      </form>

      {status && <pre>{status}</pre>}
      {otpInfo && <div style={{marginTop:8, background:'#071b2b', padding:8, borderRadius:8}}>
        <p>Prototype OTP (returned): <b>{otpInfo.otp}</b></p>
        <p>Next: verify via OTP page or call /api/verify-otp</p>
      </div>}
    </div>
  )
}
