import React from 'react';
import Button from './Button';

function LoanRequest() {
  return (
    <div className="card">
      <h2>Request a Loan</h2>
      <form>
        <input type="number" placeholder="Amount (₹)" required />
        <input type="date" placeholder="Due Date" required />
        <Button className="btn-primary" type="submit">Request Loan</Button>
      </form>
      <div className="status">
        <h3>Loan Status</h3>
        <p>Status: Pending</p>
      </div>
    </div>
  );
}

export default LoanRequest;
