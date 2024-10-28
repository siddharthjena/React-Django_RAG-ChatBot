import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const Register = ({ onRegister }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetch('http://localhost:8000/api/register/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (response.ok) {
            onRegister(data.token, username); // Pass the token and username to the parent component
        } else {
            alert(data.error);
        }
    };

    return (
      <div>
          <div className=" d-flex justify-content-center align-items-center" style={{
            background: 'linear-gradient(to bottom right, #000000, #808080)', height: '750px', // Black to grey gradient
        }}>
            <div className="bg-light p-4 rounded" style={{ width: '400px' }}>
                <h2 className="text-center" style={{ fontSize: '2rem' }}>Register</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <input 
                            type="text" 
                            className="form-control" 
                            placeholder="Username" 
                            value={username} 
                            onChange={(e) => setUsername(e.target.value)} 
                            required 
                        />
                    </div>
                    <div className="mb-3">
                        <input 
                            type="password" 
                            className="form-control" 
                            placeholder="Password" 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)} 
                            required 
                        />
                    </div>
                    <button type="submit" className="btn btn-primary w-100">Register</button>
                </form>
            </div>
        </div>
      </div>
    );
};

export default Register;
