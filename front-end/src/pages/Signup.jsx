import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Signup.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const Signup = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setError('');
    navigate('/login');
  };

  return (
    <div className="signup-container">
      <div className="signup-box">
        {/* <img src={logo} alt="JobQuest Logo" className="signup-logo" /> */}
        <h1 className="signup-title">Sign Up</h1>
        <form className="signup-form" onSubmit={handleSubmit}>
          <label htmlFor="name">Name</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name"
            required
          />
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your password"
            required
          />
          {error && <div className="signup-error">{error}</div>}
          <button type="submit" className="signup-btn">Sign Up</button>
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