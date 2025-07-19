import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Signup.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const Signup = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated, loading } = useAuth();
  
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !loading) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, loading, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error on input change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.first_name || !formData.last_name || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // Prepare data for GraphQL backend
      const registrationData = {
        username: formData.email.split('@')[0], // Generate username from email
        email: formData.email,
        firstName: formData.first_name,
        lastName: formData.last_name,
        password: formData.password
      };

      const result = await register(registrationData);
      
      if (result.success) {
        navigate('/dashboard', { replace: true });
      } else {
        // Handle GraphQL errors (array of error messages)
        if (result.errors && result.errors.length > 0) {
          setError(result.errors[0]); // Show first error
        } else {
          setError('Registration failed. Please try again.');
        }
      }
    } catch (error) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-box">
        {/* <img src={logo} alt="JobQuest Logo" className="signup-logo" /> */}
        <h1 className="signup-title">Sign Up</h1>
        <form className="signup-form" onSubmit={handleSubmit}>
          <label htmlFor="first_name">First Name</label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleInputChange}
            placeholder="Enter your first name"
            disabled={isSubmitting}
            required
          />
          <label htmlFor="last_name">Last Name</label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleInputChange}
            placeholder="Enter your last name"
            disabled={isSubmitting}
            required
          />
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="Enter your email"
            disabled={isSubmitting}
            required
          />
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            placeholder="Enter your password (min. 8 characters)"
            disabled={isSubmitting}
            required
          />
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleInputChange}
            placeholder="Confirm your password"
            disabled={isSubmitting}
            required
          />
          {error && <div className="signup-error">{error}</div>}
          <button type="submit" className="signup-btn" disabled={isSubmitting}>
            {isSubmitting ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>
        <div className="signup-footer">
          <span>Already have an account? </span>
          <Link to="/login">Login</Link>
        </div>
      </div>
    </div>
  );
};

export default Signup; 