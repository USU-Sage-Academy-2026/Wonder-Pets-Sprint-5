//Basic owner dashboard, shows event hosts basic data
import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '../api/client.js';

export default function OwnerView() {
  const [data, setData] = useState(null);
  const [message, setMessage] = useState('');

  function load() {
    apiGet('/api/owner/dashboard').then(setData).catch((err) => setMessage(err.message));
  }
  useEffect(load, []);

  async function markNoShows() {
    try {
      const res = await apiPost('/api/owner/no-shows');
      setMessage(`Marked ${res.marked} no-shows`);
      load();
    } catch (err) {
      setMessage(err.message);
    }
  }

  if (!data) return <p>{message || 'Loading...'}</p>;

  const total = (key) => data.events.reduce((sum, e) => sum + e[key], 0);
  const booked = total('booked_people');
  const noShows = total('no_shows');

  return (
    <div>
      <h1>Owner dashboard</h1>
      <p>Booked: {booked}</p>
      <p>Checked in: {total('checked_in')}</p>
      <p>No-shows: {noShows}</p>
      <p>No-show %: {booked ? ((100 * noShows) / booked).toFixed(1) : 0}%</p>

      <button onClick={markNoShows}>Mark no-shows</button>
      <p>{message}</p>

      <h2>Events</h2>
      <table>
        <thead><tr><th>Event</th><th>Booked</th><th>Checked in</th><th>No-shows</th></tr></thead>
        <tbody>
          {data.events.map((e) => (
            <tr key={e.event_id}><td>{e.event_name}</td><td>{e.booked_people}</td><td>{e.checked_in}</td><td>{e.no_shows}</td></tr>
          ))}
        </tbody>
      </table>

      <h2>Bookings by source</h2>
      <table>
        <thead><tr><th>Source</th><th>Bookings</th></tr></thead>
        <tbody>
          {data.sources.map((s) => <tr key={s.source}><td>{s.source}</td><td>{s.bookings}</td></tr>)}
        </tbody>
      </table>
    </div>
  );
}
