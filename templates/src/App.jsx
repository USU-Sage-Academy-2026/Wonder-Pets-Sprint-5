import { BrowserRouter, Routes, Route, Link } from 'react-router';
import { useEffect, useState } from 'react';
import HomePage from './pages/HomePage.jsx';
import EventPage from './pages/EventPage.jsx';
import ConfirmationPage from './pages/ConfirmationPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import SignupPage from './pages/SignupPage.jsx';
import BookingPage from './pages/BookingPage.jsx';
import StaffScanPage from './pages/StaffScanPage.jsx';
import OwnerView from './pages/OwnerView.jsx';

export default function App() {
  const [darkMode, setDarkMode] = useState(() => {
  const saved = localStorage.getItem('theme');

  if (saved) return saved === 'dark';

    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const theme = darkMode ? 'dark' : 'light';

    document.documentElement.dataset.theme = theme;
    localStorage.setItem('theme', theme);
  }, [darkMode]);
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Events</Link> | <Link to="/my-bookings">My bookings</Link> |{' '}
        <Link to="/staff/scan">Staff check-in placeholder</Link> | <Link to="/owner">Owner</Link> |{' '}
        <Link to="/login">Log in</Link> | <Link to="/signup">Sign up</Link>
        <button
          onClick={() => setDarkMode(!darkMode)}
          aria-label="Toggle dark mode"
        >
          {darkMode ? 'Destroy Eyes' : 'Dark Mode'}
        </button>
      </nav>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/events/:id" element={<EventPage />} />
        <Route path="/confirmation" element={<ConfirmationPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/my-bookings" element={<BookingPage />} />
        <Route path="/staff/scan" element={<StaffScanPage />} />
        <Route path="/owner" element={<OwnerView />} />
      </Routes>
    </BrowserRouter>
  );
}
