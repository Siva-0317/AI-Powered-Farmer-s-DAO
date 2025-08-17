// front/src/pages/LandRegistration.jsx
import React, { useState } from 'react'
import { apiPost, apiGet } from '../api'

export default function LandRegistration({ session }){
  const [form, setForm] = useState({ registration_no: '', land_name:'', size_acres:'', crop_type:'Wheat', plots_count:1 })
  const [image, setImage] = useState(null)
  const [geo, setGeo] = useState({ lat: null, lon: null })
  const [msg, setMsg] = useState(null)

  async function getGeo(){
    if(!navigator.geolocation){ setMsg('Geolocation not supported'); return }
    navigator.geolocation.getCurrentPosition(pos => {
      setGeo({ lat: pos.coords.latitude, lon: pos.coords.longitude })
      setMsg(`Location captured: ${pos.coords.latitude.toFixed(5)}, ${pos.coords.longitude.toFixed(5)}`)
    }, err => setMsg('Geolocation denied or failed'))
  }

  const submit = async(e)=>{
    e.preventDefault()
    const fd = new FormData()
    fd.append('registration_no', form.registration_no)
    fd.append('land_name', form.land_name)
    fd.append('size_acres', form.size_acres)
    fd.append('crop_type', form.crop_type)
    fd.append('plots_count', form.plots_count)
    if(image) fd.append('verification_image', image)
    if(geo.lat) {
      fd.append('geo_lat', geo.lat)
      fd.append('geo_lon', geo.lon)
    }
    const res = await apiPost('/api/add-land', fd, true)
    if (!res.ok) setMsg('Error: ' + (res.error || 'unknown'))
    else setMsg('Added: ' + JSON.stringify(res.data))
  }

  return (
    <div className="card">
      <h2>Land Registration</h2>
      <form onSubmit={submit}>
        <label>Registration No <input value={form.registration_no} onChange={e=>setForm({...form, registration_no:e.target.value})} /></label>
        <label>Land name <input value={form.land_name} onChange={e=>setForm({...form, land_name:e.target.value})} /></label>
        <label>Size (acres) <input value={form.size_acres} onChange={e=>setForm({...form, size_acres:e.target.value})} /></label>
        <label>Crop Type
          <select value={form.crop_type} onChange={e=>setForm({...form, crop_type:e.target.value})}>
            <option>Wheat</option>
            <option>Maize</option>
            <option>Rice</option>
          </select>
        </label>
        <label>Plots Count <input type="number" value={form.plots_count} onChange={e=>setForm({...form, plots_count:e.target.value})} /></label>

        <label>Verification Image <input type="file" accept="image/*" onChange={e=>setImage(e.target.files[0])} /></label>

        <div style={{marginTop:8}}>
          <button type="button" onClick={getGeo}>Capture Geolocation</button>
          <small style={{marginLeft:8}}>{geo.lat ? `${geo.lat.toFixed(5)}, ${geo.lon.toFixed(5)}` : 'No location'}</small>
        </div>

        <button type="submit">Add Land</button>
      </form>

      {msg && <pre>{msg}</pre>}
    </div>
  )
}
