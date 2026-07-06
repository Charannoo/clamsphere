function sendMessage() {
    const input = document.getElementById('userInput');
    const msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, 'user');
    input.value = '';

    fetch('/chatbot/api/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ message: msg }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            addMessage('Error: ' + data.error, 'bot');
        } else {
            addMessage(data.response, 'bot');
        }
    })
    .catch(() => {
        addMessage("Couldn't reach the server. Check your connection.", 'bot');
    });
}

function addMessage(text, sender) {
    const container = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = sender === 'user' ? 'msg msg-user' : 'msg msg-bot';
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : '';
}

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('userInput');
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') sendMessage();
    });
});
