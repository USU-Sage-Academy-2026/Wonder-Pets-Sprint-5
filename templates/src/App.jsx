import { useState } from 'react';

export default function App() {
  const [showForm, setShowForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [first, setFirst] = useState('');
  const [last, setLast] = useState('');
  const [phone, setPhone] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(e) { // SUBMIT BUTTON API, CHECK HERE FOR BASICS
    e.preventDefault(); // stop the browser reloading the page
    setMessage('Sending...');
    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({email: email, password: password, first_name: first, last_name: last, phone_number: phone}),
      });
      const data = await res.json();
      if (!res.ok) {
        setMessage(`Error ${res.status}: ${data.error}`);
      } else {
        setMessage(`Account created: ${JSON.stringify(data)}`);
      }
    } catch (err) {
      setMessage(`Could not reach the API: ${err.message}`);
    }
  }

  if (!showForm) {
    return <button onClick={() => setShowForm(true)}>Create account</button>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Email
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      </label>
      <label>
        Password
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </label>
      <label>
        First Name
        <input type="first" value={first} onChange={(e) => setFirst(e.target.value)} />
      </label>
      <label>
        Last Name
        <input type="last" value={last} onChange={(e) => setLast(e.target.value)} />
      </label>
      <label>
        Phone
        <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
      </label>
      <button type="submit">Sign up</button>
      <p>{message}</p>
    </form>
  );
}
