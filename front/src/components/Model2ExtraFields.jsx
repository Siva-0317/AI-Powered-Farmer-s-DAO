import React from 'react'

export default function Model2ExtraFields({ values, onChange, cropType, setCropType }){
  const set = (k, v) => onChange({...values, [k]: v})
  return (
    <div className="card">
      <h3>Extra inputs (Model 2)</h3>
      <div className="row">
        <label>Expected_Yield <input type="number" step="0.01" value={values.Expected_Yield||''} onChange={e=>set('Expected_Yield', e.target.value)} /></label>
        <label>Crop_Stress_Indicator <input type="number" step="0.1" value={values.Crop_Stress_Indicator||''} onChange={e=>set('Crop_Stress_Indicator', e.target.value)} /></label>
        <label>Canopy_Coverage <input type="number" step="0.1" value={values.Canopy_Coverage||''} onChange={e=>set('Canopy_Coverage', e.target.value)} /></label>
        <label>Pest_Damage <input type="number" step="0.1" value={values.Pest_Damage||''} onChange={e=>set('Pest_Damage', e.target.value)} /></label>
        <label>Leaf_Area_Index (optional) <input type="number" step="0.01" value={values.Leaf_Area_Index||''} onChange={e=>set('Leaf_Area_Index', e.target.value)} /></label>
        <label>Crop Type
          <select value={cropType} onChange={e=>setCropType(e.target.value)}>
            <option value="">(auto from selected land)</option>
            <option>Wheat</option>
            <option>Maize</option>
            <option>Rice</option>
          </select>
        </label>
      </div>
    </div>
  )
}
