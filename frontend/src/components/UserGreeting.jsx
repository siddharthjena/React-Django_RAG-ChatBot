// src/components/UserGreeting.jsx
import React from 'react';

const UserGreeting = ({ username }) => {
    return (
        <div className="alert alert-success"  style={{fontSize:'30px'}}>
            Welcome, {username}!
        </div>
    );
};

export default UserGreeting;
