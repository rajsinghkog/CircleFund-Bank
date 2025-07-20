import React, { useEffect, useState } from 'react';

function JoinGroup() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [groupId, setGroupId] = useState('');
  const [message, setMessage] = useState('');
  const [groupDetails, setGroupDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState('');

  useEffect(() => {
    async function fetchGroups() {
      try {
        const res = await fetch('/api/groups');
        const data = await res.json();
        if (data.groups) {
          setGroups(data.groups);
        } else {
          setError('Could not fetch groups');
        }
      } catch (err) {
        setError('Could not fetch groups');
      } finally {
        setLoading(false);
      }
    }
    fetchGroups();
  }, []);

  useEffect(() => {
    if (!groupId) {
      setGroupDetails(null);
      setDetailsError('');
      return;
    }
    setDetailsLoading(true);
    setDetailsError('');
    setGroupDetails(null);
    fetch(`/api/groups/${groupId}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          setDetailsError(data.error);
          setGroupDetails(null);
        } else {
          setGroupDetails(data);
        }
      })
      .catch(() => {
        setDetailsError('Could not fetch group details');
        setGroupDetails(null);
      })
      .finally(() => setDetailsLoading(false));
  }, [groupId]);

  const handleGroupSelect = (id) => {
    setGroupId(id);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    if (!name || !phone || !groupId) {
      setError('Please fill all fields.');
      return;
    }
    const res = await fetch('/api/groups/join', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, group_id: groupId })
    });
    const data = await res.json();
    if (data.message) {
      setMessage(data.message);
      setError('');
    } else {
      setError(data.error || 'Could not join group');
      setMessage('');
    }
  };

  return (
    <div className="card">
      <h2>Join a Lending Circle</h2>
      <div style={{ marginBottom: '2rem' }}>
        <h3>Available Groups</h3>
        {loading ? (
          <p>Loading groups...</p>
        ) : error ? (
          <p style={{ color: 'red' }}>{error}</p>
        ) : groups.length === 0 ? (
          <p>No groups available.</p>
        ) : (
          <ul>
            {groups.map(group => (
              <li key={group.id} style={{ marginBottom: '0.5rem', cursor: 'pointer' }}
                  onClick={() => handleGroupSelect(group.id)}>
                <strong>{group.name}</strong> &mdash; ₹{group.contribution_amount} ({group.cycle})
                {groupId === group.id && <span style={{color:'#6366f1',marginLeft:8}}>(Selected)</span>}
              </li>
            ))}
          </ul>
        )}
        {groupId && (
          <div style={{marginTop:'1rem'}}>
            <h4>Group Details</h4>
            {detailsLoading ? (
              <p>Loading details...</p>
            ) : detailsError ? (
              <p style={{color:'red'}}>{detailsError}</p>
            ) : groupDetails ? (
              <div style={{background:'#fff',padding:'1rem',borderRadius:'0.5rem',boxShadow:'0 1px 4px #e0e7ff'}}>
                <p><strong>Name:</strong> {groupDetails.name}</p>
                <p><strong>Contribution Amount:</strong> ₹{groupDetails.contribution_amount}</p>
                <p><strong>Cycle:</strong> {groupDetails.cycle}</p>
                <p><strong>Group ID:</strong> {groupDetails.id}</p>
              </div>
            ) : null}
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Your Name"
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
          type="text"
          placeholder="Group Code"
          value={groupId}
          onChange={e => setGroupId(e.target.value)}
          required
        />
        <button className="btn-primary" type="submit">Join Group</button>
      </form>
      {message && <p style={{color:'green'}}>{message}</p>}
      {error && <p style={{color:'red'}}>{error}</p>}
    </div>
  );
}

export default JoinGroup;
