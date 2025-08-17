import React, { useState } from "react";
import { apiPost } from "../api";
import WalletConnect from "../WalletConnect";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [form, setForm] = useState({ name: '', mobile: '', aadhaar: '', wallet_address: '', email: '' });
  const [gov, setGov] = useState(null);
  const [selfie, setSelfie] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');
  const nav = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setErr('');
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => fd.append(k, v));
    if (gov) fd.append('gov_id_file', gov);
    if (selfie) fd.append('selfie_file', selfie);
    const res = await apiPost('/api/register', fd, true);
    setLoading(false);
    if (res.ok) {
      // Show OTP for prototype/demo
      alert(`Registered!\nRegistration No: ${res.data.registration_no}\nOTP: ${res.data.otp}\n\n(OTP shown only for demo)`);
      nav('/verify-otp', { state: { registration_no: res.data.registration_no, otp: res.data.otp } });
    } else {
      setErr(res.error || 'Registration failed');
    }
  }

  return (
    <div className="card">
      <h2>Register Farmer</h2>
      <WalletConnect onConnected={({ address }) => setForm({ ...form, wallet_address: address })} />
      <form onSubmit={submit}>
        <label>Name<input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></label>
        <label>Mobile<input required value={form.mobile} onChange={e => setForm({ ...form, mobile: e.target.value })} /></label>
        <label>Aadhaar<input required value={form.aadhaar} onChange={e => setForm({ ...form, aadhaar: e.target.value })} /></label>
        <label>Email<input required value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></label>
        <label>Wallet<input required value={form.wallet_address} onChange={e => setForm({ ...form, wallet_address: e.target.value })} /></label>
        <label>Gov ID<input type="file" accept="image/*" required onChange={e => setGov(e.target.files[0])} /></label>
        <label>Selfie<input type="file" accept="image/*" required onChange={e => setSelfie(e.target.files[0])} /></label>
        <button type="submit" disabled={loading}>{loading ? "Registering..." : "Register"}</button>
      </form>
      {err && <div style={{ color: "red" }}>{err}</div>}
    </div>
  );
}