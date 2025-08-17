import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiGet, apiPost } from '../api'
import SharedFields from '../components/SharedFields'
import Model2ExtraFields from '../components/Model2ExtraFields'

export default function Claim({ session }){
  const nav = useNavigate()
  const [lands, setLands] = useState([])
  const [landId, setLandId] = useState('')
  const [shared, setShared] = useState({})
  const [extra, setExtra] = useState({})
  const [cropType, setCropType] = useState('')
  const [res, setRes] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(()=>{
    if(!session){ nav('/login'); return }
    (async()=>{
      const q = await apiGet(`/api/lands?farmer_id=${session.farmer_id}`)
      if(q.ok) setLands(q.data || [])
    })()
  }, [session])

  const submit = async ()=>{
    setErr(null); setRes(null)
    if(!landId){ setErr('Select a land'); return }

    const m2 = { ...extra }
    if(cropType) m2.Crop_Type = cropType

    const payload = {
      farmer_id: session.farmer_id,
      land_id: Number(landId),
      model1: shared,
      model2: m2
    }

    const r = await apiPost('/api/claims/submit', payload)
    if(!r.ok) { setErr(r.error || 'claim failed'); return }
    setRes(r.data)
  }

  const addLand = async () => {
    const land_name = prompt('land name (e.g., siva-land1)')
    const crop_type = prompt('Crop type (Wheat/Maize/Rice)')
    if(!land_name || !crop_type) return
    const r = await apiPost('/api/lands', { farmer_id: session.farmer_id, land_name, crop_type, location: '' })
    if(r.ok){
      const q = await apiGet(`/api/lands?farmer_id=${session.farmer_id}`)
      if(q.ok) setLands(q.data)
    } else setErr(JSON.stringify(r))
  }

  return (
    <div>
      <div className="card">
        <h2>Submit Claim</h2>
        <div>
          <label>Select Land:
            <select value={landId} onChange={e=>setLandId(e.target.value)}>
              <option value="">Select</option>
              {lands.map(l => <option key={l.id} value={l.id}>{l.land_name} — {l.crop_type}</option>)}
            </select>
            <button onClick={addLand} style={{marginLeft:12}}>+ Add Land</button>
          </label>
        </div>
      </div>

      <SharedFields values={shared} onChange={setShared} />
      <Model2ExtraFields values={extra} onChange={setExtra} cropType={cropType} setCropType={setCropType} />

      <div className="card">
        <button onClick={submit}>Run Prediction & Submit</button>
      </div>

      {err && <div className="card"><pre>{err}</pre></div>}
      {res && <div className="card"><h3>Result</h3><pre>{JSON.stringify(res, null, 2)}</pre></div>}
    </div>
  )
}
