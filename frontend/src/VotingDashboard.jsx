import React from 'react';

function VotingDashboard() {
  return (
    <div className="card">
      <h2>Voting Dashboard</h2>
      <div className="loan-list">
        <div className="loan-item">
          <p>Loan Request by Alice - ₹1000</p>
          <button className="btn-yes">Vote Yes</button>
          <button className="btn-no">Vote No</button>
        </div>
        <div className="loan-item">
          <p>Loan Request by Bob - ₹500</p>
          <button className="btn-yes">Vote Yes</button>
          <button className="btn-no">Vote No</button>
        </div>
      </div>
    </div>
  );
}

export default VotingDashboard;
