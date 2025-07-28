import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import client from './apolloClient';
import Login from './pages/Login';
import Signup from './pages/Signup';
import JobListings from './pages/JobListings';
import JobApplicationForm from './pages/JobApplicationForm';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import JobDetails from './pages/JobDetails';
import SavedJobs from './pages/SavedJobs';
import ApplicationHistory from './pages/ApplicationHistory';
import Settings from './pages/Settings';
import CreateJob from './pages/CreateJob';
import NavBar from './components/NavBar';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import { JobProvider } from './context/JobContext';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import CompanyProfile from './pages/CompanyProfile';
import InterviewPrepEnhanced from './pages/InterviewPrepEnhanced';
import ResumeBuilder from './pages/ResumeBuilder';
import AISuggestions from './pages/AISuggestions';
import SkillsAndCertificationsEnhanced from './pages/SkillsAndCertificationsEnhanced';
import LearningPaths from './pages/LearningPaths';
import UploadJobEnhanced from './pages/UploadJobEnhanced';
import ResumeVersions from './pages/ResumeVersions';
import MyJobs from './pages/MyJobs';
import SkillJobMapping from './pages/SkillJobMapping';
import EditJob from './pages/EditJob';
import CompanySearch from './pages/CompanySearch';
import NotFound from './pages/NotFound';
import AuthTest from './pages/AuthTest';
import ServicesTest from './pages/ServicesTest';
import './App.css';
import './styles/mobile.css';

function App() {
  return (
    <ErrorBoundary>
      <ApolloProvider client={client}>
        <AuthProvider>
          <JobProvider>
            <ToastProvider>
              <Router>
          <NavBar />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/auth-test" element={<AuthTest />} />
            <Route path="/services-test" element={<ServicesTest />} />
            
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
                <InterviewPrepEnhanced />
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
                <SkillsAndCertificationsEnhanced />
              </ProtectedRoute>
            } />
            <Route path="/learning-paths" element={
              <ProtectedRoute>
                <LearningPaths />
              </ProtectedRoute>
            } />
            <Route path="/upload-job" element={
              <ProtectedRoute>
                <UploadJobEnhanced />
              </ProtectedRoute>
            } />
            <Route path="/resume-versions" element={
              <ProtectedRoute>
                <ResumeVersions />
              </ProtectedRoute>
            } />
            <Route path="/create-job" element={
              <ProtectedRoute>
                <CreateJob />
              </ProtectedRoute>
            } />
            <Route path="/my-jobs" element={
              <ProtectedRoute>
                <MyJobs />
              </ProtectedRoute>
            } />
            <Route path="/skill-job-mapping" element={
              <ProtectedRoute>
                <SkillJobMapping />
              </ProtectedRoute>
            } />
            <Route path="/edit-job/:jobId" element={
              <ProtectedRoute>
                <EditJob />
              </ProtectedRoute>
            } />
            <Route path="/company-search" element={
              <ProtectedRoute>
                <CompanySearch />
              </ProtectedRoute>
            } />
            
            {/* 404 page */}
            <Route path="*" element={<NotFound />} />
          </Routes>
              </Router>
            </ToastProvider>
          </JobProvider>
        </AuthProvider>
      </ApolloProvider>
    </ErrorBoundary>
  );
}

export default App;
