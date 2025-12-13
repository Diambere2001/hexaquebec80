const bubble = document.getElementById("ai-bubble");
const chat = document.getElementById("ai-chat");
const chatBody = document.getElementById("chat-body");
const sendBtn = document.getElementById("send-btn");
const input = document.getElementById("user-input");
const formContainer = document.getElementById("ai-form");

let messageEnvoye = false;

/* ---- Ouvrir / Fermer chatbot ---- */
if (bubble) {
    bubble.onclick = () => {

        const isClosed = chat.style.display === "none";
        chat.style.display = isClosed ? "block" : "none";

        if (isClosed && chatBody) {
            chatBody.innerHTML = `
                <div class="bot-msg">
                    👋 Bonjour, je suis le représentant du <b>soutien technique HexaQuébec</b>.<br><br>
                    Expliquez votre problème dans la zone de message ci-dessous.<br>
                    Après votre message, un formulaire apparaîtra si nécessaire.<br><br>
                    Merci !
                </div>
            `;
        }
    };
}

/* ---- Envoi du message utilisateur ---- */
if (sendBtn) {
    sendBtn.onclick = () => {

        let msg = input.value.trim();
        if (!msg) return;

        messageEnvoye = true;

        chatBody.innerHTML += `<div class="user-msg">${msg}</div>`;
        chatBody.scrollTop = chatBody.scrollHeight;
        input.value = "";

        // Détection des mots clés
        const text = msg.toLowerCase();

        if (
            text.includes("problème") ||
            text.includes("bug") ||
            text.includes("erreur") ||
            text.includes("technique")
        ) {
            chatBody.innerHTML += `
                <div class="bot-msg">
                    👍 Je comprends votre situation.<br>
                    Pour mieux vous aider, veuillez remplir ce formulaire :
                </div>
            `;

            if (formContainer) {
                formContainer.style.display = "block";
            }
        }
    };
}

/* ============= FORMULAIRE TECHNIQUE =================== */
const chatbotForm = document.getElementById("chatbot-form");

if (chatbotForm) {
    chatbotForm.onsubmit = (e) => {
        e.preventDefault();

        if (!messageEnvoye) {
            alert("Veuillez d’abord envoyer un message avant de remplir le formulaire.");
            return;
        }

        let formData = new FormData(chatbotForm);

        fetch("/chatbot_form/", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(response => {

            formContainer.style.display = "none";

            chatBody.innerHTML += `
                <div class="bot-msg">
                    ✅ Merci ! Votre message et votre formulaire ont été transmis à l’équipe HexaQuébec.<br>
                    Nous vous répondrons sous peu.
                </div>
            `;

            chatBody.scrollTop = chatBody.scrollHeight;
            chatbotForm.reset();
        });
    };
}
