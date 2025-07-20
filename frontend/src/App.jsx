import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import JoinGroup from './JoinGroup';
import Deposit from './Deposit';
import LoanRequest from './LoanRequest';
import VotingDashboard from './VotingDashboard';
import RepaymentTracker from './RepaymentTracker';
import Signup from './Signup';
import Profile from './Profile';
import './App.css';

function Navbar() {
  return (
    <nav className="navbar">
      <h1>CircleFund Bank</h1>
      <ul>
        <li><Link to="/">Join Group</Link></li>
        <li><Link to="/deposit">Deposit</Link></li>
        <li><Link to="/loan">Loan Request</Link></li>
        <li><Link to="/voting">Voting Dashboard</Link></li>
        <li><Link to="/repayment">Repayment Tracker</Link></li>
        <li><Link to="/signup">Signup</Link></li>
        <li><Link to="/profile">Profile</Link></li>
      </ul>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<JoinGroup />} />
          <Route path="/deposit" element={<Deposit />} />
          <Route path="/loan" element={<LoanRequest />} />
          <Route path="/voting" element={<VotingDashboard />} />
          <Route path="/repayment" element={<RepaymentTracker />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
