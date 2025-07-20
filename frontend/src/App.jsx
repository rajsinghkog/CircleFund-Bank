import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, NavLink } from 'react-router-dom';
import { FaUsers, FaPiggyBank, FaHandHoldingUsd, FaVoteYea, FaHistory, FaUserPlus, FaSignInAlt, FaSignOutAlt, FaUserCircle } from 'react-icons/fa';
import JoinGroup from './JoinGroup';
import Deposit from './Deposit';
import LoanRequest from './LoanRequest';
import VotingDashboard from './VotingDashboard';
import RepaymentTracker from './RepaymentTracker';
import Signup from './Signup';
import Profile from './Profile';
import Signin from './Signin';
import './App.css';

function Navbar({ isLoggedIn, onLogout, user }) {
  const [logoutPressed, setLogoutPressed] = useState(false);
  return (
    <nav className="navbar">
      <h1>CircleFund Bank</h1>
      <ul>
        <li><NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}><FaUsers style={{verticalAlign:'middle',marginRight:6}}/>Join Group</NavLink></li>
        <li><NavLink to="/deposit" className={({ isActive }) => isActive ? 'active' : ''}><FaPiggyBank style={{verticalAlign:'middle',marginRight:6}}/>Deposit</NavLink></li>
        <li><NavLink to="/loan" className={({ isActive }) => isActive ? 'active' : ''}><FaHandHoldingUsd style={{verticalAlign:'middle',marginRight:6}}/>Loan Request</NavLink></li>
        <li><NavLink to="/voting" className={({ isActive }) => isActive ? 'active' : ''}><FaVoteYea style={{verticalAlign:'middle',marginRight:6}}/>Voting Dashboard</NavLink></li>
        <li><NavLink to="/repayment" className={({ isActive }) => isActive ? 'active' : ''}><FaHistory style={{verticalAlign:'middle',marginRight:6}}/>Repayment Tracker</NavLink></li>
        {!isLoggedIn && <li><NavLink to="/signup" className={({ isActive }) => isActive ? 'active' : ''}><FaUserPlus style={{verticalAlign:'middle',marginRight:6}}/>Signup</NavLink></li>}
        {!isLoggedIn && <li><NavLink to="/signin" className={({ isActive }) => isActive ? 'active' : ''}><FaSignInAlt style={{verticalAlign:'middle',marginRight:6}}/>Signin</NavLink></li>}
        {isLoggedIn && user && <li style={{color:'#a5b4fc',fontWeight:'bold',marginRight:'1rem'}}><FaUserCircle style={{verticalAlign:'middle',marginRight:6}}/>Hello, {user.name}</li>}
        {isLoggedIn && <li><button
          onClick={async () => { setLogoutPressed(true); await onLogout(); setLogoutPressed(false); }}
          className={logoutPressed ? 'pressed' : ''}
          style={{background:'none',border:'none',color:'#6366f1',cursor:'pointer'}}
        ><FaSignOutAlt style={{verticalAlign:'middle',marginRight:6}}/>Sign Out</button></li>}
      </ul>
    </nav>
  );
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check login status and fetch user info on mount
    fetch('/api/me', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setIsLoggedIn(!!data.user);
        setUser(data.user || null);
      })
      .catch(() => {
        setIsLoggedIn(false);
        setUser(null);
      });
  }, []);

  const handleLogout = async () => {
    await fetch('/api/signout', { method: 'POST', credentials: 'include' });
    setIsLoggedIn(false);
    setUser(null);
  };

  return (
    <Router>
      <Navbar isLoggedIn={isLoggedIn} onLogout={handleLogout} user={user} />
      <div className="container">
        <Routes>
          <Route path="/" element={<JoinGroup />} />
          <Route path="/deposit" element={<Deposit />} />
          <Route path="/loan" element={<LoanRequest />} />
          <Route path="/voting" element={<VotingDashboard />} />
          <Route path="/repayment" element={<RepaymentTracker />} />
          <Route path="/signup" element={<Signup setIsLoggedIn={setIsLoggedIn} setUser={setUser} />} />
          <Route path="/signin" element={<Signin />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
