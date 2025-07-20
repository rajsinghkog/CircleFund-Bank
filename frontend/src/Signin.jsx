import React, { useState, useEffect } from 'react';
import Button from './Button';

function Signin() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    fetch('/api/me', { credentials: 'include' })
      .then(res => res.json())
      .then(data => setIsLoggedIn(!!data.user))
      .catch(() => setIsLoggedIn(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    const res = await fetch('/api/signin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password }),
      credentials: 'include' // Ensure cookies are sent/received
    });
    const data = await res.json();
    if (data.user) {
      setMessage('Signin successful!');
      setIsLoggedIn(true);
    } else {
      setMessage(data.error || 'Signin failed');
      setIsLoggedIn(false);
    }
  };

  const handleSignout = async () => {
    const res = await fetch('/api/signout', {
      method: 'POST',
      credentials: 'include'
    });
    const data = await res.json();
    setMessage(data.message || 'Signed out');
    setIsLoggedIn(false);
  };

  return (
    <div className="signin-container">
      <h2>Sign In</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Phone Number"
          value={phone}
          onChange={e => setPhone(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <Button className="btn-primary" type="submit">Sign In</Button>
      </form>
      {message && <p>{message}</p>}
      {isLoggedIn && <Button className="btn-primary" type="button" onClick={handleSignout} style={{marginTop: '1rem'}}>Sign Out</Button>}
    </div>
  );
}

export default Signin; 