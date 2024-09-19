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

function setJsonData(data, valid) {
    container = document.getElementById("workflowCode");
    container.innerHTML = data
    hljs.highlightBlock(container);

    container = document.getElementById("jsonValid");
    container.innerHTML = ((valid) ? '✅' : '❌');
}

async function displayJsonWorkflow() {
   const response = await fetch(`/chat/${currentSessionId}/workflow`);
   const workflow = await response.json();
   setJsonData(JSON.stringify(workflow.document, null, 2), workflow.valid)

   render_workflow(
        document.getElementById("renderWorkflow"),
        JSON.stringify(workflow.document));

}

// Display messages in the chat area
function displayMessages(messages) {
    const chatMessages = document.getElementById('chatMessages');
    while (chatMessages.firstChild) {
        chatMessages.removeChild(chatMessages.firstChild);
    }
    messages.forEach(message => {
        const messageDiv = createElement('div', `message ${message.type}`);
        messageDiv.innerHTML = marked.parse(message.content);
        chatMessages.appendChild(messageDiv);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
    hljs.highlightAll();
    displayJsonWorkflow();
}

// Send a message and handle streaming response
async function sendMessage(message) {


    const chatMessages = document.getElementById('chatMessages');
    const hummanMessageDiv = createElement('div', 'message');
    chatMessages.appendChild(hummanMessageDiv);
    hummanMessageDiv.innerHTML = marked.parse(message);

    const url = currentSessionId
        ? `/chat/${currentSessionId}`
        : 'chat';
    const response = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({input: message})
    });

    if (!currentSessionId) {
        currentSessionId = response.headers.get('session_id');
    }

    // This is for streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let aiMessage = '';
    const aiMessageDiv = createElement('div', 'message ai');
    chatMessages.appendChild(aiMessageDiv);
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        aiMessage += chunk;
        aiMessageDiv.innerHTML = marked.parse(aiMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        hljs.highlightAll();
    }

    loadChat(currentSessionId);
    return { messages: [{ type: 'ai', content: aiMessage }] };
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

// Resize textarea by default
document.getElementById('messageInput').addEventListener('input', function(e) {
    e.target.style.height = 'auto'; // Reset height
    e.target.style.height = e.target.scrollHeight + 'px'; 
});

// Initial load
fetchChats();
