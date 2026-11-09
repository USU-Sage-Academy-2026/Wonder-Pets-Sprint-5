// Sends every request to Flask and handles errors
//Add api here so it can be reused in other pages.
async function request(method, path, body) {
  const res = await fetch(path, {
    method,
    credentials: 'include',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.error || `Error ${res.status}`);
  return data;
}

export const apiGet = (path) => request('GET', path);
export const apiPost = (path, body = {}) => request('POST', path, body);