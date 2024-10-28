import React, { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import Chat from './components/Chat';
import UserGreeting from './components/UserGreeting'; // Import the new UserGreeting component
import 'bootstrap/dist/css/bootstrap.min.css';

const App = () => {
    const [token, setToken] = useState(null);
    const [username, setUsername] = useState(''); // State to store the username
    const [isRegistering, setIsRegistering] = useState(true); // State to toggle between Register and Login

    const toggleForm = () => {
        setIsRegistering(!isRegistering); // Toggle the form
    };

    const handleRegister = (token, username) => {
        setToken(token);
        setUsername(username);
    };

    const handleLogin = (token, username) => {
        setToken(token);
        setUsername(username);
    };

    return (
        <div>
            {!token ? (
                <div>
                    {isRegistering ? (
                        <>
                            <Register onRegister={handleRegister} />
                            <p>
                                Already have an account?{' '}
                                <button onClick={toggleForm}>Login</button>
                            </p>
                        </>
                    ) : (
                        <>
                            <Login onLogin={handleLogin} />
                            <p>
                                Don't have an account?{' '}
                                <button onClick={toggleForm}>Register</button>
                            </p>
                        </>
                    )}
                </div>
            ) : (
                <div>
                    <UserGreeting username={username} /> {/* Display welcome message */}
                    <Chat token={token} />
                </div>
            )}
        </div>
    );
};

export default App;
