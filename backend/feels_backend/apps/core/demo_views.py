"""
Never, never, never use this code in production XDDDD
"""

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json


@method_decorator(csrf_exempt, name='dispatch')
class DemoView(View):
    """Simple HTML demo interface for testing the API"""
    
    def get(self, request):
        """Serve demo HTML page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feels Backend API Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4a5568;
            margin-bottom: 30px;
            text-align: center;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            background: #f7fafc;
        }
        .section h2 {
            color: #2d3748;
            margin-top: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #4a5568;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            font-size: 14px;
            box-sizing: border-box;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        button:hover {
            background: #5a67d8;
        }
        .response {
            margin-top: 15px;
            padding: 15px;
            border-radius: 8px;
            white-space: pre-wrap;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }
        .success {
            background: #f0fff4;
            border: 1px solid #9ae6b4;
            color: #22543d;
        }
        .error {
            background: #fed7d7;
            border: 1px solid #feb2b2;
            color: #742a2a;
        }
        .token-display {
            background: #edf2f7;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: monospace;
            word-break: break-all;
            font-size: 12px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Feels Backend API Demo</h1>
        
        <div class="section">
            <h2>🔐 Authentication</h2>
            <div class="grid">
                <div>
                    <h3>Register</h3>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="reg-username" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" id="reg-email" placeholder="Enter email">
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="reg-password" placeholder="Enter password">
                    </div>
                    <div class="form-group">
                        <label>Display Name:</label>
                        <input type="text" id="reg-display-name" placeholder="Enter display name">
                    </div>
                    <button onclick="register()">Register</button>
                    <div id="reg-response" class="response" style="display:none;"></div>
                </div>
                
                <div>
                    <h3>Login</h3>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="login-username" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="login-password" placeholder="Enter password">
                    </div>
                    <button onclick="login()">Login</button>
                    <div id="login-response" class="response" style="display:none;"></div>
                </div>
            </div>
            
            <div id="token-section" style="display:none;">
                <h3>🎫 Current Token</h3>
                <div id="current-token" class="token-display"></div>
                <button onclick="logout()">Logout</button>
                <button onclick="getProfile()">Get Profile</button>
            </div>
        </div>

        <div class="section">
            <h2>📝 Posts</h2>
            <div class="grid">
                <div>
                    <h3>Create Post</h3>
                    <div class="form-group">
                        <label>Body:</label>
                        <textarea id="post-body" placeholder="What are you feeling?" rows="3"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Feeling:</label>
                        <select id="post-feeling">
                            <option value="Happy">😊 Happy</option>
                            <option value="Sad">😢 Sad</option>
                            <option value="Excited">🤗 Excited</option>
                            <option value="Anxious">😰 Anxious</option>
                            <option value="Grateful">🙏 Grateful</option>
                            <option value="Frustrated">😤 Frustrated</option>
                            <option value="Content">😌 Content</option>
                            <option value="Lonely">😔 Lonely</option>
                            <option value="Motivated">💪 Motivated</option>
                            <option value="Overwhelmed">😵 Overwhelmed</option>
                            <option value="Peaceful">☮️ Peaceful</option>
                            <option value="Angry">😠 Angry</option>
                            <option value="Hopeful">🌟 Hopeful</option>
                            <option value="Confused">🤔 Confused</option>
                            <option value="Proud">😎 Proud</option>
                            <option value="Disappointed">😞 Disappointed</option>
                        </select>
                    </div>
                    <button onclick="createPost()">Create Post</button>
                    <div id="post-response" class="response" style="display:none;"></div>
                </div>
                
                <div>
                    <h3>Get Posts</h3>
                    <button onclick="getPosts()">Get All Posts</button>
                    <div id="posts-response" class="response" style="display:none;"></div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>👥 Social</h2>
            <div class="grid">
                <div>
                    <h3>Send Friend Request</h3>
                    <div class="form-group">
                        <label>Username to send request:</label>
                        <input type="text" id="friend-username" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label>Message (optional):</label>
                        <input type="text" id="friend-message" placeholder="Want to be friends?">
                    </div>
                    <button onclick="sendFriendRequest()">Send Friend Request</button>
                    <div id="friend-response" class="response" style="display:none;"></div>
                </div>
                
                <div>
                    <h3>Manage Friend Requests</h3>
                    <button onclick="getFriendRequests('received')">Get Received Requests</button>
                    <button onclick="getFriendRequests('sent')">Get Sent Requests</button>
                    <button onclick="getFriendRequests('all')">Get All Requests</button>
                    <div id="friend-requests-response" class="response" style="display:none;"></div>
                </div>
            </div>
            
            <div class="grid">
                <div>
                    <h3>Accounts</h3>
                    <button onclick="getAccounts()">Get All Accounts</button>
                    <div id="accounts-response" class="response" style="display:none;"></div>
                </div>
                
                <div>
                    <h3>Feelings</h3>
                    <button onclick="getFeelings()">Get All Feelings</button>
                    <div id="feelings-response" class="response" style="display:none;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentToken = null;
        const BASE_URL = 'http://localhost:8000/api';

        function showResponse(elementId, data, isError = false) {
            const element = document.getElementById(elementId);
            element.style.display = 'block';
            element.className = `response ${isError ? 'error' : 'success'}`;
            element.textContent = JSON.stringify(data, null, 2);
        }

        function updateTokenDisplay(token) {
            currentToken = token;
            const tokenSection = document.getElementById('token-section');
            const tokenDisplay = document.getElementById('current-token');
            
            if (token) {
                tokenSection.style.display = 'block';
                tokenDisplay.textContent = token;
            } else {
                tokenSection.style.display = 'none';
                tokenDisplay.textContent = '';
            }
        }

        async function makeRequest(url, options = {}) {
            try {
                if (currentToken && !options.headers) {
                    options.headers = {};
                }
                if (currentToken) {
                    options.headers['Authorization'] = `Bearer ${currentToken}`;
                }
                
                const response = await fetch(url, options);
                const data = await response.json();
                return { data, status: response.status, ok: response.ok };
            } catch (error) {
                return { data: { error: error.message }, status: 0, ok: false };
            }
        }

        async function register() {
            const data = {
                action: 'register',
                username: document.getElementById('reg-username').value,
                email: document.getElementById('reg-email').value,
                password: document.getElementById('reg-password').value,
                display_name: document.getElementById('reg-display-name').value
            };

            const result = await makeRequest(`${BASE_URL}/auth/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            showResponse('reg-response', result.data, !result.ok);
            
            if (result.ok && result.data.token) {
                updateTokenDisplay(result.data.token);
            }
        }

        async function login() {
            const data = {
                action: 'login',
                username: document.getElementById('login-username').value,
                password: document.getElementById('login-password').value
            };

            const result = await makeRequest(`${BASE_URL}/auth/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            showResponse('login-response', result.data, !result.ok);
            
            if (result.ok && result.data.token) {
                updateTokenDisplay(result.data.token);
            }
        }

        async function logout() {
            const result = await makeRequest(`${BASE_URL}/auth/`, {
                method: 'DELETE'
            });

            if (result.ok) {
                updateTokenDisplay(null);
                alert('Logged out successfully');
            } else {
                alert('Logout failed: ' + JSON.stringify(result.data));
            }
        }

        async function getProfile() {
            const result = await makeRequest(`${BASE_URL}/profile/`);
            showResponse('login-response', result.data, !result.ok);
        }

        async function createPost() {
            const data = {
                body: document.getElementById('post-body').value,
                feeling_name: document.getElementById('post-feeling').value
            };

            const result = await makeRequest(`${BASE_URL}/posts/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            showResponse('post-response', result.data, !result.ok);
        }

        async function getPosts() {
            const result = await makeRequest(`${BASE_URL}/posts/`);
            showResponse('posts-response', result.data, !result.ok);
        }

        async function sendFriendRequest() {
            const username = document.getElementById('friend-username').value;
            if (!username) {
                showResponse('friend-response', { error: 'Please enter a username' }, true);
                return;
            }

            // First get the user's UID by username
            const accountResult = await makeRequest(`${BASE_URL}/accounts/?username=${username}`);
            if (!accountResult.ok || !accountResult.data.accounts || accountResult.data.accounts.length === 0) {
                showResponse('friend-response', { error: 'User not found' }, true);
                return;
            }

            const receiverUid = accountResult.data.accounts[0].uid;
            const message = document.getElementById('friend-message').value || 'Want to be friends?';

            const data = {
                receiver_uid: receiverUid,
                message: message
            };

            const result = await makeRequest(`${BASE_URL}/friend-requests/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            showResponse('friend-response', result.data, !result.ok);
        }

        async function getFriendRequests(type = 'received') {
            const result = await makeRequest(`${BASE_URL}/friend-requests/?type=${type}`);
            
            if (result.ok && result.data.friend_requests) {
                // Add action buttons for received requests
                const requestsWithActions = result.data.friend_requests.map(req => {
                    if (type === 'received' && req.status === 'pending') {
                        return {
                            ...req,
                            actions: `
                                <button onclick="respondToFriendRequest('${req.uid}', 'accept')" style="background: #27ae60; color: white; border: none; padding: 5px 10px; margin: 2px; border-radius: 3px; cursor: pointer;">Accept</button>
                                <button onclick="respondToFriendRequest('${req.uid}', 'reject')" style="background: #e74c3c; color: white; border: none; padding: 5px 10px; margin: 2px; border-radius: 3px; cursor: pointer;">Reject</button>
                            `
                        };
                    }
                    return req;
                });
                
                showResponse('friend-requests-response', { 
                    friend_requests: requestsWithActions, 
                    count: result.data.count,
                    type: type 
                }, false);
            } else {
                showResponse('friend-requests-response', result.data, !result.ok);
            }
        }

        async function respondToFriendRequest(requestId, action) {
            const data = { action: action };

            const result = await makeRequest(`${BASE_URL}/friend-requests/${requestId}/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            showResponse('friend-requests-response', result.data, !result.ok);
            
            // Refresh the friend requests list
            if (result.ok) {
                setTimeout(() => getFriendRequests('received'), 1000);
            }
        }

        async function getFeelings() {
            const result = await makeRequest(`${BASE_URL}/feelings/`);
            showResponse('feelings-response', result.data, !result.ok);
        }

        async function getAccounts() {
            const result = await makeRequest(`${BASE_URL}/accounts/`);
            showResponse('accounts-response', result.data, !result.ok);
        }

        // Generate random username for testing
        document.getElementById('reg-username').value = 'user' + Math.floor(Math.random() * 10000);
        document.getElementById('reg-email').value = 'test' + Math.floor(Math.random() * 10000) + '@example.com';
        document.getElementById('reg-display-name').value = 'Test User ' + Math.floor(Math.random() * 1000);
    </script>
</body>
</html>
        """
        return HttpResponse(html)
