import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import Login from './pages/Login';
import Signup from './pages/Signup';
import JobListings from './pages/JobListings';
import JobApplicationForm from './pages/JobApplicationForm';
import JobMap from './pages/JobMap';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import JobDetails from './pages/JobDetails';
import SavedJobs from './pages/SavedJobs';
import ApplicationHistory from './pages/ApplicationHistory';
import Settings from './pages/Settings';
import NavBar from './components/NavBar';
import ProtectedRoute from './components/ProtectedRoute';
import { JobProvider } from './context/JobContext';
import { AuthProvider } from './context/AuthContext';
import CompanyProfile from './pages/CompanyProfile';
import InterviewPrep from './pages/InterviewPrep';
import ResumeBuilder from './pages/ResumeBuilder';
import AISuggestions from './pages/AISuggestions';
import SkillsAndCertifications from './pages/SkillsAndCertifications';
import NotFound from './pages/NotFound';
import client from './apolloClient';
import './App.css';

function App() {
  return (
    <ApolloProvider client={client}>
      <AuthProvider>
        <JobProvider>
          <Router>
          <NavBar />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            
            {/* Protected routes */}
            <Route path="/jobs" element={
              <ProtectedRoute>
                <JobListings />
              </ProtectedRoute>
            } />
            <Route path="/jobs/:jobId" element={
              <ProtectedRoute>
                <JobDetails />
              </ProtectedRoute>
            } />
            <Route path="/apply/:jobId" element={
              <ProtectedRoute>
                <JobApplicationForm />
              </ProtectedRoute>
            } />
            <Route path="/map" element={
              <ProtectedRoute>
                <JobMap />
              </ProtectedRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
            <Route path="/saved-jobs" element={
              <ProtectedRoute>
                <SavedJobs />
              </ProtectedRoute>
            } />
            <Route path="/application-history" element={
              <ProtectedRoute>
                <ApplicationHistory />
              </ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } />
            <Route path="/company/:companyId" element={
              <ProtectedRoute>
                <CompanyProfile />
              </ProtectedRoute>
            } />
            <Route path="/interview-prep" element={
              <ProtectedRoute>
                <InterviewPrep />
              </ProtectedRoute>
            } />
            <Route path="/resume-builder" element={
              <ProtectedRoute>
                <ResumeBuilder />
              </ProtectedRoute>
            } />
            <Route path="/ai-suggestions" element={
              <ProtectedRoute>
                <AISuggestions />
              </ProtectedRoute>
            } />
            <Route path="/skills" element={
              <ProtectedRoute>
                <SkillsAndCertifications />
              </ProtectedRoute>
            } />
            
            {/* 404 page */}
            <Route path="*" element={<NotFound />} />
          </Routes>
          </Router>
        </JobProvider>
      </AuthProvider>
    </ApolloProvider>
  );
}

export default App;
