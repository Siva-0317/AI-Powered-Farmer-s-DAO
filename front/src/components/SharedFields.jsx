import React from 'react'

export default function SharedFields({ values, onChange }){
  const set = (k, v) => onChange({...values, [k]: v})
  return (
    <div className="card">
      <h3>Shared inputs (Model 1)</h3>
      <div className="row">
        <label>NDVI <input type="number" step="0.001" value={values.NDVI||''} onChange={e=>set('NDVI', e.target.value)} /></label>
        <label>SAVI <input type="number" step="0.001" value={values.SAVI||''} onChange={e=>set('SAVI', e.target.value)} /></label>
        <label>Chlorophyll_Content <input type="number" step="0.01" value={values.Chlorophyll_Content||''} onChange={e=>set('Chlorophyll_Content', e.target.value)} /></label>
        <label>Leaf_Area_Index <input type="number" step="0.01" value={values.Leaf_Area_Index||''} onChange={e=>set('Leaf_Area_Index', e.target.value)} /></label>
        <label>Temperature <input type="number" step="0.1" value={values.Temperature||''} onChange={e=>set('Temperature', e.target.value)} /></label>
        <label>Humidity <input type="number" step="0.1" value={values.Humidity||''} onChange={e=>set('Humidity', e.target.value)} /></label>
        <label>Rainfall <input type="number" step="0.1" value={values.Rainfall||''} onChange={e=>set('Rainfall', e.target.value)} /></label>
        <label>Soil_Moisture <input type="number" step="0.1" value={values.Soil_Moisture||''} onChange={e=>set('Soil_Moisture', e.target.value)} /></label>
      </div>
    </div>
  )
}
