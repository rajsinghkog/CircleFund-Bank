import React, { useState } from 'react';
import Button from './Button';

function Signup({ setIsLoggedIn, setUser }) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, password })
    });
    const data = await res.json();
    setMessage(data.message || data.error);
    if (data.message && !data.error) {
      // Signup successful, now sign in automatically
      const signinRes = await fetch('/api/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, password }),
        credentials: 'include'
      });
      const signinData = await signinRes.json();
      if (signinData.user) {
        setIsLoggedIn(true);
        setUser(signinData.user);
      }
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={e => setName(e.target.value)}
          required
        />
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
        <Button className="btn-primary" type="submit">Sign Up</Button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Signup;
