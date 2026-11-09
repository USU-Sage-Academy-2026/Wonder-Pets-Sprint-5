//Events, also has a signup that shows up if not logged in for guests
import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router';
import { apiGet, apiPost } from '../api/client.js';

export default function EventPage() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loggedIn, setLoggedIn] = useState(false);
  const [people, setPeople] = useState([{ first_name: '', birth_date: '' }]);
  const [guest, setGuest] = useState({ first_name: '', last_name: '', email: '', phone: '' });
  const [howHeard, setHowHeard] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiGet(`/api/events/${id}`).then(setEvent).catch((err) => setError(err.message));
    apiGet('/api/me').then((me) => setLoggedIn(me.logged_in)).catch(() => {});
  }, [id]);

  function setPartySize(n) {
    setPeople((old) => Array.from({ length: n }, (_, i) => old[i] || { first_name: '', birth_date: '' }));
  }
  function setPerson(i, field, value) {
    setPeople((old) => old.map((p, j) => (j === i ? { ...p, [field]: value } : p)));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      const res = await apiPost('/api/registrations', {
        event_id: event.event_id,
        attendees: people,
        guest: loggedIn ? null : guest,
        how_heard: howHeard,
        src: searchParams.get('src'),
      });
      if (res.warnings && res.warnings.length > 0) setResult(res);
      else navigate(`/confirmation?code=${res.confirmation_code}`);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!event) return <p>{error || 'Loading...'}</p>;

  if (result) {
    return (
      <div>
        <p>Booked. Warnings:</p>
        <ul>{result.warnings.map((w) => <li key={w}>{w}</li>)}</ul>
        <button onClick={() => navigate(`/confirmation?code=${result.confirmation_code}`)}>Continue</button>
      </div>
    );
  }

  return (
    <div>
      <h1>{event.event_name}</h1>
      <p>{new Date(event.start_time).toLocaleString()} – {new Date(event.end_time).toLocaleString()}</p>
      <p>{event.location_name}</p>
      <p>${event.price} · {event.spots_left} spots left</p>
      {event.age_rule !== 'none' && <p>Ages {event.min_age ?? 0}{event.max_age != null ? `–${event.max_age}` : '+'} ({event.age_rule})</p>}
      <p>{event.description}</p>

      <h2>Book</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Party size
          <input type="number" min="1" max={event.max_party_size} value={people.length}
            onChange={(e) => setPartySize(Math.max(1, Number(e.target.value)))} />
        </label>

        {people.map((p, i) => (
          <div key={i}>
            <p>Person {i + 1}</p>
            <label>Name <input value={p.first_name} onChange={(e) => setPerson(i, 'first_name', e.target.value)} /></label>
            <label>Birth date <input type="date" value={p.birth_date} onChange={(e) => setPerson(i, 'birth_date', e.target.value)} /></label>
          </div>
        ))}

        {!loggedIn && (
          <div>
            <p>Your contact details</p>
            <label>First name <input value={guest.first_name} onChange={(e) => setGuest({ ...guest, first_name: e.target.value })} /></label>
            <label>Last name <input value={guest.last_name} onChange={(e) => setGuest({ ...guest, last_name: e.target.value })} /></label>
            <label>Email <input type="email" value={guest.email} onChange={(e) => setGuest({ ...guest, email: e.target.value })} /></label>
            <label>Phone <input value={guest.phone} onChange={(e) => setGuest({ ...guest, phone: e.target.value })} /></label>
          </div>
        )}

        <label>
          How did you hear about us?
          <input value={howHeard} onChange={(e) => setHowHeard(e.target.value)} />
        </label>

        <button type="submit">Book</button>
        {error && <p>{error}</p>}
      </form>
    </div>
  );
}
