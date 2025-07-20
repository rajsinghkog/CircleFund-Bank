import React from 'react';
import Button from './Button';

function VotingDashboard() {
  return (
    <div className="card">
      <h2>Voting Dashboard</h2>
      <div className="loan-list">
        <div className="loan-item">
          <p>Loan Request by Alice - ₹1000</p>
          <Button className="btn-yes">Vote Yes</Button>
          <Button className="btn-no">Vote No</Button>
        </div>
        <div className="loan-item">
          <p>Loan Request by Bob - ₹500</p>
          <Button className="btn-yes">Vote Yes</Button>
          <Button className="btn-no">Vote No</Button>
        </div>
      </div>
    </div>
  );
}

export default VotingDashboard;
