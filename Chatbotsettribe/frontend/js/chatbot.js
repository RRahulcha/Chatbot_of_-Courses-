document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const clearChatBtn = document.getElementById("clear-chat-btn");
    const apiUrl = "http://127.0.0.1:8000/api/chat/";
    const sessionId = getSessionId();
    const historyKey = `settribe_chat_history_${sessionId}`;
    let messages = loadMessages();

    function renderMessages() {
        chatMessages.replaceChildren();
        for (const message of messages) {
            const msgDiv = document.createElement("div");
            msgDiv.className = `message ${message.role === "user" ? "user-msg" : "bot-msg"}`;
            msgDiv.textContent = message.content;
            chatMessages.appendChild(msgDiv);
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendMessage(content, role) {
        messages.push({ role, content });
        sessionStorage.setItem(historyKey, JSON.stringify(messages));
        renderMessages();
    }

    function loadMessages() {
        try {
            const saved = JSON.parse(sessionStorage.getItem(historyKey) || "[]");
            if (Array.isArray(saved) && saved.every(message => message.role && message.content)) {
                return saved;
            }
        } catch (error) {
            sessionStorage.removeItem(historyKey);
        }
        return [{
            role: "assistant",
            content: "Hi! I am the SETTribe AI Assistant. I can help with courses, internships, fees and careers."
        }];
    }

    function showTypingIndicator() {
        const msgDiv = document.createElement("div");
        msgDiv.id = "typing-indicator";
        msgDiv.className = "message bot-msg typing-indicator";
        msgDiv.textContent = "SETTribe AI Assistant is typing...";
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        document.getElementById("typing-indicator")?.remove();
    }

    renderMessages();

    function getSessionId() {
        let id = sessionStorage.getItem("settribe_session_id");
        if (!id) {
            id = crypto.randomUUID();
            sessionStorage.setItem("settribe_session_id", id);
        }
        return id;
    }

    async function sendMessage(event) {
        event.preventDefault();
        const text = userInput.value.trim();
        if (!text || sendBtn.disabled) {
            return;
        }

        appendMessage(text, "user");
        userInput.value = "";
        sendBtn.disabled = true;
        showTypingIndicator();

        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId, message: text })
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "The chat request failed.");
            }

            appendMessage(data.answer || "I could not generate a response.", "assistant");
        } catch (error) {
            appendMessage(`Unable to reach the chatbot: ${error.message}`, "assistant");
        } finally {
            removeTypingIndicator();
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    chatForm.addEventListener("submit", sendMessage);

    clearChatBtn.addEventListener("click", () => {
        messages = [];
        sessionStorage.removeItem(historyKey);
        appendMessage(
            "Hi! I am the SETTribe AI Assistant. I can help with courses, internships, fees and careers.",
            "assistant"
        );
        userInput.focus();
    });
});
