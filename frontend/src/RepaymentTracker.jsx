import React from 'react';

function RepaymentTracker() {
  return (
    <div className="card">
      <h2>Repayment Tracker</h2>
      <table className="repayment-table">
        <thead>
          <tr>
            <th>Loan ID</th>
            <th>Amount</th>
            <th>Due Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1</td>
            <td>₹1000</td>
            <td>2025-08-01</td>
            <td>Pending</td>
          </tr>
          <tr>
            <td>2</td>
            <td>₹500</td>
            <td>2025-07-25</td>
            <td>Repaid</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default RepaymentTracker;
