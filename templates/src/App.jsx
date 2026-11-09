import { BrowserRouter, Routes, Route, Link } from 'react-router';
import HomePage from './pages/HomePage.jsx';
import EventPage from './pages/EventPage.jsx';
import ConfirmationPage from './pages/ConfirmationPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import SignupPage from './pages/SignupPage.jsx';
import BookingPage from './pages/BookingPage.jsx';
import StaffScanPage from './pages/StaffScanPage.jsx';
import OwnerView from './pages/OwnerView.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Events</Link> | <Link to="/my-bookings">My bookings</Link> |{' '}
        <Link to="/staff/scan">Staff check-in placeholder</Link> | <Link to="/owner">Owner</Link> |{' '}
        <Link to="/login">Log in</Link> | <Link to="/signup">Sign up</Link>
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
