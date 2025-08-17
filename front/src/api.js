export async function apiPost(path, body, isForm=false){
  const opts = {
    method: 'POST',
    headers: isForm ? {} : { 'Content-Type': 'application/json' },
    body: isForm ? body : JSON.stringify(body)
  };
  const res = await fetch(path, opts);
  try { return await res.json() } catch(e) { return { ok: false, error: 'invalid json' } }
}

export async function apiGet(path){
  const res = await fetch(path);
  try { return await res.json() } catch(e) { return { ok: false, error: 'invalid json' } }
}
