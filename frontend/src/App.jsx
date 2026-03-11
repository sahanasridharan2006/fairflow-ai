import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DriverDashboard from './pages/DriverDashboard';
import DriverFeedback from './pages/DriverFeedback';
import DriverHistory from './pages/DriverHistory';
import DriverSignup from './pages/DriverSignup';
import AdminSignup from './pages/AdminSignup';
import DriverLayout from './components/DriverLayout';
import AdminDashboard from './pages/AdminDashboard';
import Login from './pages/Login';
import RoleSelection from './pages/RoleSelection';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RoleSelection />} />
        <Route path="/login/driver" element={<Login role="driver" />} />
        <Route path="/login/admin" element={<Login role="admin" />} />
        <Route path="/signup/driver" element={<DriverSignup />} />
        <Route path="/signup/admin" element={<AdminSignup />} />

        {/* Driver Routes Wrapped in Layout */}
        <Route path="/driver" element={<DriverLayout />}>
          <Route index element={<DriverDashboard />} />
          <Route path="feedback" element={<DriverFeedback />} />
          <Route path="history" element={<DriverHistory />} />
        </Route>

        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
