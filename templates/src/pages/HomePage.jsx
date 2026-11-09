import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { apiGet } from '../api/client.js';

export default function HomePage() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    apiGet('/api/events').then(setEvents).catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <h1>Events</h1>
      {error && <p>{error}</p>}
      {events.length === 0 && !error && <p>No events.</p>}
      {events.map((e) => (
        <div key={e.event_id}>
          <h2><Link to={`/events/${e.event_id}`}>{e.event_name}</Link></h2>
          <p>{new Date(e.start_time).toLocaleString()}</p>
          <p>${e.price}, Only {e.spots_left} spots left</p>
          {e.age_rule !== 'none' && <p>Ages {e.min_age ?? 0}{e.max_age != null ? `–${e.max_age}` : '+'} ({e.age_rule})</p>} // age limits
        </div>
      ))}
    </div>
  );
}
