import React from 'react';

function LoanRequest() {
  return (
    <div className="card">
      <h2>Request a Loan</h2>
      <form>
        <input type="number" placeholder="Amount (₹)" required />
        <input type="date" placeholder="Due Date" required />
        <button className="btn-primary" type="submit">Request Loan</button>
      </form>
      <div className="status">
        <h3>Loan Status</h3>
        <p>Status: Pending</p>
      </div>
    </div>
  );
}

export default LoanRequest;
