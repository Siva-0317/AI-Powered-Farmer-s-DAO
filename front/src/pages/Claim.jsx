import React,{useEffect, useState} from "react"; import { apiGet, apiPost } from "../api"; import { useNavigate } from "react-router-dom";
export default function Claim({session}){ const nav=useNavigate(); const [lands,setLands]=useState([]); const [landId,setLandId]=useState(''); const [shared,setShared]=useState({}); const [extra,setExtra]=useState({}); const [msg,setMsg]=useState('');
  useEffect(()=>{ if(!session) return; (async()=>{ const r=await apiGet(`/api/lands?farmer_id=${session.farmer_id}`); if(r.ok) setLands(r.data); else setMsg('Could not fetch lands') })() },[session]);

  async function checkPayout(){
    if(!session) { setMsg('Login first'); return }
    if(!landId) { setMsg('Select land'); return }
    const payload={ registration_no: session.registration_no, land_id: Number(landId), model1: shared, model2: extra }
    const r = await apiPost('/api/claims/submit', payload);
    if(!r.ok){ setMsg('Err: '+(r.error||'')); return }
    // show onchain tx if present
    const on = r.data.onchain;
    setMsg('Prediction: '+JSON.stringify(r.data, null, 2) + '\nOnchain: '+JSON.stringify(on));
    nav('/payout', { state: { result: r.data } });
  }

  return (<div className="card"><h2>Submit Claim</h2><label>Select Land<select value={landId} onChange={e=>setLandId(e.target.value)}><option value="">Select</option>{lands.map(l=> <option key={l.id} value={l.id}>{l.land_name} - {l.crop_type}</option>)}</select></label><h3>Shared inputs (model1)</h3><label>NDVI<input onChange={e=>setShared({...shared,NDVI:parseFloat(e.target.value)})} /></label><label>SAVI<input onChange={e=>setShared({...shared,SAVI:parseFloat(e.target.value)})} /></label><label>Chlorophyll<input onChange={e=>setShared({...shared,Chlorophyll_Content:parseFloat(e.target.value)})} /></label><label>LAI<input onChange={e=>setShared({...shared,Leaf_Area_Index:parseFloat(e.target.value)})} /></label><label>Temp<input onChange={e=>setShared({...shared,Temperature:parseFloat(e.target.value)})} /></label><label>Humidity<input onChange={e=>setShared({...shared,Humidity:parseFloat(e.target.value)})} /></label><label>Rainfall<input onChange={e=>setShared({...shared,Rainfall:parseFloat(e.target.value)})} /></label><label>Soil Moisture<input onChange={e=>setShared({...shared,Soil_Moisture:parseFloat(e.target.value)})} /></label><h3>Extra (model2)</h3><label>Expected Yield<input onChange={e=>setExtra({...extra,Expected_Yield:parseFloat(e.target.value)})} /></label><label>Crop Stress Indicator<input onChange={e=>setExtra({...extra,Crop_Stress_Indicator:parseFloat(e.target.value)})} /></label><label>Canopy Coverage<input onChange={e=>setExtra({...extra,Canopy_Coverage:parseFloat(e.target.value)})} /></label><label>Pest Damage<input onChange={e=>setExtra({...extra,Pest_Damage:parseFloat(e.target.value)})} /></label><label>Crop Type<select onChange={e=>setExtra({...extra,Crop_Type:e.target.value})}><option>Wheat</option><option>Maize</option><option>Rice</option></select></label><div><button onClick={checkPayout}>Check Payout</button></div><pre>{msg}</pre></div>)
}
