import React, { useState } from "react";
import { apiPost } from "../api";
import { useNavigate, useLocation } from "react-router-dom";

export default function Login({ onLogin }) {
  const [reg, setReg] = useState('');
  const nav = useNavigate();
  const location = useLocation();
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (location.state?.registration_no) {
      setReg(location.state.registration_no);
    }
  }, [location.state]);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setErr('');
    const res = await apiPost('/api/login', { registration_no: reg });
    setLoading(false);
    if (!res.ok) {
      setErr(res.error || 'Login failed');
      return;
    }
    if (onLogin) onLogin(res.data);
    nav('/claim');
  }

  return (
    <div className="card">
      <h2>Login</h2>
      <form onSubmit={submit}>
        <label>Registration No
          <input required value={reg} onChange={e => setReg(e.target.value)} />
        </label>
        <button disabled={loading}>{loading ? "Signing in..." : "Sign In"}</button>
      </form>
      <pre style={{ color: "red" }}>{err}</pre>
    </div>
  );
}