import React, { useState } from "react";
import { apiPost } from "../api";
import { useLocation, useNavigate } from "react-router-dom";

export default function VerifyOTP() {
  const location = useLocation();
  const nav = useNavigate();
  const [registration_no, setReg] = useState(location.state?.registration_no || "");
  const [otp, setOtp] = useState(location.state?.otp || "");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setMsg("");
    const res = await apiPost('/api/verify-otp', { registration_no, otp });
    setLoading(false);
    if (res.ok) {
      setMsg("Verified! Redirecting to login...");
      setTimeout(() => nav('/login', { state: { registration_no } }), 1200);
    } else {
      setMsg("Error: " + (res.error || 'Verification failed'));
    }
  }

  // If user lands here without registration_no, redirect to register
  React.useEffect(() => {
    if (!registration_no) nav('/register');
  }, [registration_no, nav]);

  return (
    <div className="card">
      <h2>Verify OTP</h2>
      <form onSubmit={submit}>
        <label>Registration No
          <input required value={registration_no} onChange={e => setReg(e.target.value)} />
        </label>
        <label>OTP
          <input required value={otp} onChange={e => setOtp(e.target.value)} />
        </label>
        <button disabled={loading}>{loading ? "Verifying..." : "Verify"}</button>
      </form>
      <pre>{msg}</pre>
    </div>
  );
}