import React from 'react';

function Deposit() {
  return (
    <div className="card">
      <h2>Deposit ₹5</h2>
      <form>
        <input type="number" placeholder="Amount (₹)" min="5" defaultValue={5} required />
        <button className="btn-primary" type="submit">Deposit</button>
      </form>
      <div className="history">
        <h3>Deposit History</h3>
        <ul>
          <li>2025-07-01: ₹5</li>
          <li>2025-07-08: ₹5</li>
        </ul>
      </div>
    </div>
  );
}

export default Deposit;
