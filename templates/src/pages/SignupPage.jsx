//simplified sign-up page
import { useState } from 'react';
import { apiPost } from '../api/client.js';

export default function SignupPage() {
  const [form, setForm] = useState({ email: '', password: '', first_name: '', last_name: '', phone_number: '' });
  const [message, setMessage] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const data = await apiPost('/api/auth/signup', form);
      setMessage(`Account created for ${data.first_name}`);
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <div>
      <h1>Sign up</h1>
      <form onSubmit={handleSubmit}>
        <label>First name <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></label>
        <label>Last name <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></label>
        <label>Email <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
        <label>Phone <input value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} /></label>
        <label>Password <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
        <button type="submit">Sign up</button>
      </form>
      <p>{message}</p>
    </div>
  );
}
