// static/monapp/js/chatbot.js

function toggleChat() {
    const chatBody = document.getElementById('chatBody');
    chatBody.style.display = chatBody.style.display === 'none' ? 'block' : 'none';
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const inputElement = document.getElementById('chatInput');
    const messagesContainer = document.getElementById('chatMessages');
    const message = inputElement.value.trim();

    if (message === '') return;

    // Afficher le message de l'utilisateur
    messagesContainer.innerHTML += `
        <div class="user-message">
            <p>${message}</p>
        </div>
    `;

    inputElement.value = '';

    try {
        const response = await fetch('/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `message=${encodeURIComponent(message)}`
        });

        const data = await response.json();

        // Afficher la réponse du chatbot
        messagesContainer.innerHTML += `
            <div class="bot-message">
                <p>${data.response}</p>
            </div>
        `;

        // Scroll vers le bas
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Fonction pour obtenir le cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
