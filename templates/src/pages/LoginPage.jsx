import { useState } from 'react';
import { apiPost } from '../api/client.js';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const data = await apiPost('/api/auth/login', { email, password });
      setMessage(`Logged in as ${data.first_name} (${data.role})`);
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function handleLogout() {
    try {
      await apiPost('/api/auth/logout');
      setMessage('Logged out');
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <div>
      <h1>Log in</h1>
      <form onSubmit={handleSubmit}>
        <label>Email <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button type="submit">Log in</button>
      </form>
      <button onClick={handleLogout}>Log out</button>
      <p>{message}</p>
    </div>
  );
}
