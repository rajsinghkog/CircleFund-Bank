import React, { useState } from 'react';
import Button from './Button';

function Profile() {
  const [username, setUsername] = useState('');
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  const fetchProfile = async () => {
    const res = await fetch(`/api/me?username=${encodeURIComponent(username)}`);
    const data = await res.json();
    if (data.user) {
      setUser(data.user);
      setError('');
    } else {
      setUser(null);
      setError(data.error);
    }
  };

  return (
    <div className="profile-container">
      <h2>Profile</h2>
      <input
        type="text"
        placeholder="Enter username"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <Button onClick={fetchProfile}>Get Profile</Button>
      {user && (
        <div>
          <h3>User Info</h3>
          <p>Username: {user.username}</p>
        </div>
      )}
      {error && <p style={{color: 'red'}}>{error}</p>}
    </div>
  );
}

export default Profile;
