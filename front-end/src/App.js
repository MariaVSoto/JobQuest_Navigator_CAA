import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import JobListings from './pages/JobListings';
import JobApplicationForm from './pages/JobApplicationForm';
import JobMap from './pages/JobMap';
import Dashboard from './pages/Dashboard';
import NavBar from './components/NavBar';
import { JobProvider } from './context/JobContext';
import './App.css';

function App() {
  return (
    <JobProvider>
      <Router>
        <NavBar />
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/jobs" element={<JobListings />} />
          <Route path="/apply/:jobId" element={<JobApplicationForm />} />
          <Route path="/map" element={<JobMap />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Router>
    </JobProvider>
  );
}

export default App;
