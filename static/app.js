// Global variables
let currentSessionId = null;


marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(lang, code).value;
    } else {
      return hljs.highlightAuto(code).value;
    }
  }
});


// Helper function to create DOM elements
function createElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
}

// Fetch all chats
async function fetchChats() {
    const response = await fetch('/chat');
    const chats = await response.json();
    const chatList = document.getElementById('chatList');
    chatList.innerHTML = '';
    chats.forEach(chat => {
        const li = createElement('li', '', chat);
        li.addEventListener('click', () => loadChat(chat));
        chatList.appendChild(li);
    });
}

// Load a specific chat
async function loadChat(sessionId) {
    currentSessionId = sessionId;
    const response = await fetch(`/chat/${sessionId}`);
    const messages = await response.json();
    displayMessages(messages);
}

// Display messages in the chat area
function displayMessages(messages) {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '';
    messages.forEach(message => {
        const messageDiv = createElement('div', `message ${message.type}`);
        messageDiv.innerHTML = marked.parse(message.content);
        chatMessages.appendChild(messageDiv);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
    console.log("This is the call for this");
    hljs.highlightAll();
}

// Send a message
async function sendMessage(message) {
    const url = currentSessionId 
        ? `/chat/${currentSessionId}`
        : 'chat';
    const response = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({input: message})
    });
    const data = await response.json();
    if (!currentSessionId) {
        currentSessionId = response.headers.get('session_id');
    }
    loadChat(currentSessionId)
    //displayMessages(data.messages);
    return data;
}

// Event listeners
document.getElementById('newChatButton').addEventListener('click', () => {
    const input = document.getElementById('newChatInput');
    if (input.value.trim()) {
        currentSessionId = null;
        sendMessage(input.value);
        input.value = '';
    }
});

document.getElementById('sendButton').addEventListener('click', () => {
    const input = document.getElementById('messageInput');
    if (input.value.trim()) {
        sendMessage(input.value);
        input.value = '';
    }
});

// Initial load
fetchChats();
