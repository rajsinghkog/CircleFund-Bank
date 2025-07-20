import React from 'react';

function JoinGroup() {
  return (
    <div className="card">
      <h2>Join a Lending Circle</h2>
      <form>
        <input type="text" placeholder="Your Name" required />
        <input type="text" placeholder="Phone Number" required />
        <input type="text" placeholder="Group Code" required />
        <button className="btn-primary" type="submit">Join Group</button>
      </form>
    </div>
  );
}

export default JoinGroup;
