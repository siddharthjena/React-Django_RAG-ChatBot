import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const Chat = ({ token }) => {
    const [message, setMessage] = useState('');
    const [responses, setResponses] = useState([]);
    const [pdfFile, setPdfFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');

    const handleSend = async () => {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
            },
            body: JSON.stringify({ query: message }),
        });
        const data = await response.json();
        setLoading(false);
    
        if (response.ok) {
            // Debugging: Log the response to see its structure
            console.log("Response Data:", data);
    
            // Assuming your backend sends token usage like this:
            const tokens = {
                input: data.token_usage?.input_token_count || 0,
                output: data.token_usage?.output_token_count || 0,
                total: data.token_usage?.total_token_count || 0,
            };
    
            setResponses((prev) => [
                ...prev,
                { 
                    user: message, 
                    ai: data.response, 
                    tokens 
                }
            ]);
            setMessage(''); // Clear the input
        } else {
            alert(data.error);
        }
    };
    
    const handlePdfUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('pdf_file', file);

        setLoading(true);
        const response = await fetch('http://localhost:8000/api/chat/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
            },
            body: formData,
        });

        const data = await response.json();
        setLoading(false);

        if (response.ok) {
            setUploadStatus(data.message); // Display success message
        } else {
            alert(data.error);
        }
    };

    const handleNewChat = async () => {
        const response = await fetch('http://localhost:8000/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
            },
            body: JSON.stringify({ new_chat: true }),
        });

        if (response.ok) {
            setResponses([]); // Clear previous messages
            setUploadStatus(''); // Reset upload status
        } else {
            alert('Failed to start a new chat.');
        }
    };

    return (
        <div className="d-flex flex-column" style={{
            background: 'linear-gradient(to bottom right, #000000, #808080)', height: '550px' // Black to grey gradient
        }}>
            <div className="flex-grow-1 p-4" style={{ overflowY: 'auto' }}>
                <h2 className="text-center text-light">Chat with AI</h2>
                <div className="mb-3">
                    {responses.map((r, index) => (
                        <div key={index} className="mb-2">
                            <strong className="text-light">You:</strong> <span className="text-white">{r.user}</span>
                            <br />
                            <strong className="text-light">AI:</strong> <span className="text-white">{r.ai}</span>
                            <br />
                            <span className="text-light">Tokens - Input: <span className="text-white">{r.tokens.input}</span>, Output: <span className="text-white">{r.tokens.output}</span>, Total: <span className="text-white">{r.tokens.total}</span></span>
                        </div>
                    ))}
                </div>
                {uploadStatus && <div className="text-success">{uploadStatus}</div>}
            </div>
            <div style={{ paddingBottom: '10px' }}>
                <div className="container input-group mb-3" style={{ width: '800px' }}>
                    <input
                        type="text"
                        className="form-control"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Type your message"
                    />
                    <button className="btn btn-primary" onClick={handleSend} disabled={loading}>
                        {loading ? 'Loading...' : 'Send'}
                    </button>
                </div>
                <div className="container input-group mb-3" style={{ width: '800px' }}>
                    <input
                        type="file"
                        className="form-control"
                        accept=".pdf"
                        onChange={handlePdfUpload}
                    />
                    <button className="btn btn-secondary" onClick={handleNewChat} disabled={loading}>
                        New Chat
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Chat;
