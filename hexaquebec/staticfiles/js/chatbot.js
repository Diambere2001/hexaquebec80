const chatBody = document.getElementById("chat-body");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const notifSound = document.getElementById("notif-sound");

function addMessage(text, sender = "user") {
    const bubble = document.createElement("div");
    bubble.classList.add("message", sender);
    bubble.textContent = text;

    chatBody.appendChild(bubble);
    chatBody.scrollTop = chatBody.scrollHeight;

    // Notification sonore uniquement pour le bot
    if (sender === "bot") {
        notifSound.play();
    }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

function sendMessage() {
    const msg = input.value.trim();
    if (msg === "") return;

    addMessage(msg, "user");
    input.value = "";

    // Simuler réponse bot
    setTimeout(() => {
        addMessage("Réponse HexaQuébec : " + msg, "bot");
    }, 600);
}
