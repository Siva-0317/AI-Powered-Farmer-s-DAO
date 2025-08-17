import React,{useState} from "react"; import { apiPost } from "../api";
export default function AddLand(){
  const [form,setForm]=useState({registration_no:'',land_name:'',size_acres:'',crop_type:'Wheat',plots_count:1});
  const [image,setImage]=useState(null); const [geo,setGeo]=useState({lat:null,lon:null});
  const [msg,setMsg]=useState('');

  function captureGeo(){
    if(!navigator.geolocation){ setMsg('No geolocation'); return }
    navigator.geolocation.getCurrentPosition(p=>{ setGeo({lat:p.coords.latitude,lon:p.coords.longitude}); setMsg('Location captured') }, e=>setMsg('Geo denied'));
  }

  async function submit(e){
    e.preventDefault();
    const fd = new FormData();
    Object.entries(form).forEach(([k,v])=>fd.append(k,v));
    if(image) fd.append('verification_image', image);
    if(geo.lat){ fd.append('geo_lat', geo.lat); fd.append('geo_lon', geo.lon) }
    const res = await apiPost('/api/add-land', fd, true);
    setMsg(res.ok ? 'Added: '+JSON.stringify(res.data) : 'Err: '+(res.error||''))
  }
  return (<div className="card"><h2>Add Land</h2><form onSubmit={submit}><label>Registration<input value={form.registration_no} onChange={e=>setForm({...form,registration_no:e.target.value})} /></label><label>Landname<input value={form.land_name} onChange={e=>setForm({...form,land_name:e.target.value})} /></label><label>Size acres<input value={form.size_acres} onChange={e=>setForm({...form,size_acres:e.target.value})} /></label><label>Crop<select value={form.crop_type} onChange={e=>setForm({...form,crop_type:e.target.value})}><option>Wheat</option><option>Maize</option><option>Rice</option></select></label><label>Verification image<input type="file" accept="image/*" onChange={e=>setImage(e.target.files[0])} /></label><div><button type="button" onClick={captureGeo}>Capture Geolocation</button><small>{geo.lat?`${geo.lat}, ${geo.lon}`:''}</small></div><button type="submit">Add Land</button></form><pre>{msg}</pre></div>)
}
