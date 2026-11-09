import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { apiGet } from '../api/client.js';

export default function BookingPage() {
  const [bookings, setBookings] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    apiGet('/api/registrations/mine').then(setBookings).catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <h1>My bookings</h1>
      {error && <p>{error}</p>}
      {bookings.map((b) => (
        <div key={b.confirmation_code}>
          <h2>{b.event_name}</h2>
          <p>{new Date(b.start_time).toLocaleString()} · party of {b.party_size} · {b.status}</p>
          <Link to={`/confirmation?code=${b.confirmation_code}`}>Show QR</Link>
        </div>
      ))}
    </div>
  );
}
