document.addEventListener("DOMContentLoaded", () => {
    // Prevent duplicate initialization if the script is loaded more than once.
    if (window.settribeChatbotInitialized) {
        return;
    }
    window.settribeChatbotInitialized = true;

    const chatMessages = document.getElementById("chat-messages");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const clearChatBtn = document.getElementById("clear-chat-btn");

    const apiUrl = "http://127.0.0.1:8000/api/chat/";

    const sessionId = getSessionId();
    const historyKey = `settribe_chat_history_${sessionId}`;

    let messages = loadMessages();


    // =========================================================
    // SECURITY
    // =========================================================

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // =========================================================
    // MARKDOWN RENDERER
    // =========================================================
    // Converts the Markdown returned by the RAG/LLM into
    // readable chatbot HTML.
    //
    // Supports:
    // - Headings
    // - Bold
    // - Italic
    // - Bullet lists
    // - Numbered lists
    // - Tables
    // - Paragraphs
    // - Links
    // =========================================================

    function renderMarkdown(markdown) {
        if (!markdown) {
            return "";
        }

        let text = String(markdown)
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .trim();

        const lines = text.split("\n");

        let html = "";
        let inBulletList = false;
        let inNumberedList = false;
        let inTable = false;
        let tableRows = [];


        function closeLists() {
            if (inBulletList) {
                html += "</ul>";
                inBulletList = false;
            }

            if (inNumberedList) {
                html += "</ol>";
                inNumberedList = false;
            }
        }


        function isTableSeparator(line) {
            const value = line.trim();

            if (!value.includes("|")) {
                return false;
            }

            const cells = value
                .replace(/^\|/, "")
                .replace(/\|$/, "")
                .split("|")
                .map(cell => cell.trim());

            return cells.length > 0 &&
                cells.every(cell => /^:?-{3,}:?$/.test(cell));
        }


        function parseTableRow(line) {
            return line
                .trim()
                .replace(/^\|/, "")
                .replace(/\|$/, "")
                .split("|")
                .map(cell => cell.trim());
        }


        function renderTable(rows) {
            if (!rows || rows.length < 2) {
                return "";
            }

            const headers = rows[0];
            const bodyRows = rows.slice(1);

            let tableHtml = '<div class="chat-table-wrapper">';
            tableHtml += '<table class="chat-table">';

            tableHtml += "<thead><tr>";

            headers.forEach(header => {
                tableHtml += `<th>${formatInlineMarkdown(header)}</th>`;
            });

            tableHtml += "</tr></thead>";

            if (bodyRows.length > 0) {
                tableHtml += "<tbody>";

                bodyRows.forEach(row => {
                    tableHtml += "<tr>";

                    headers.forEach((_, index) => {
                        const cell = row[index] || "";
                        tableHtml += `<td>${formatInlineMarkdown(cell)}</td>`;
                    });

                    tableHtml += "</tr>";
                });

                tableHtml += "</tbody>";
            }

            tableHtml += "</table>";
            tableHtml += "</div>";

            return tableHtml;
        }


        function formatInlineMarkdown(value) {
            let result = escapeHtml(value);

            // Markdown links
            result = result.replace(
                /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
                '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
            );

            // Bold
            result = result.replace(
                /\*\*(.+?)\*\*/g,
                "<strong>$1</strong>"
            );

            // Bold using __
            result = result.replace(
                /__(.+?)__/g,
                "<strong>$1</strong>"
            );

            // Italic
            result = result.replace(
                /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
                "<em>$1</em>"
            );

            // Inline code
            result = result.replace(
                /`([^`]+)`/g,
                "<code>$1</code>"
            );

            return result;
        }


        function addParagraph(linesToRender) {
            const content = linesToRender
                .join(" ")
                .trim();

            if (!content) {
                return;
            }

            html += `<p>${formatInlineMarkdown(content)}</p>`;
        }


        let paragraphBuffer = [];


        for (let i = 0; i < lines.length; i++) {
            const rawLine = lines[i];
            const line = rawLine.trim();

            // Empty line
            if (!line) {
                closeLists();

                if (paragraphBuffer.length > 0) {
                    addParagraph(paragraphBuffer);
                    paragraphBuffer = [];
                }

                continue;
            }


            // -------------------------------------------------
            // TABLE
            // -------------------------------------------------

            if (
                line.includes("|") &&
                i + 1 < lines.length &&
                isTableSeparator(lines[i + 1])
            ) {
                closeLists();

                if (paragraphBuffer.length > 0) {
                    addParagraph(paragraphBuffer);
                    paragraphBuffer = [];
                }

                tableRows = [];

                tableRows.push(parseTableRow(line));

                i++;

                // Skip separator row.
                tableRows.push(parseTableRow(lines[i]));

                i++;

                while (
                    i < lines.length &&
                    lines[i].trim() &&
                    lines[i].includes("|")
                ) {
                    tableRows.push(parseTableRow(lines[i]));
                    i++;
                }

                i--;

                html += renderTable([
                    tableRows[0],
                    ...tableRows.slice(2)
                ]);

                continue;
            }


            // -------------------------------------------------
            // HEADINGS
            // -------------------------------------------------

            const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);

            if (headingMatch) {
                closeLists();

                if (paragraphBuffer.length > 0) {
                    addParagraph(paragraphBuffer);
                    paragraphBuffer = [];
                }

                const level = headingMatch[1].length;
                const headingText = formatInlineMarkdown(
                    headingMatch[2]
                );

                html += `<h${level}>${headingText}</h${level}>`;

                continue;
            }


            // -------------------------------------------------
            // BULLET LIST
            // -------------------------------------------------

            const bulletMatch = line.match(/^[-*•]\s+(.+)$/);

            if (bulletMatch) {
                if (paragraphBuffer.length > 0) {
                    addParagraph(paragraphBuffer);
                    paragraphBuffer = [];
                }

                if (inNumberedList) {
                    html += "</ol>";
                    inNumberedList = false;
                }

                if (!inBulletList) {
                    html += "<ul>";
                    inBulletList = true;
                }

                html += `<li>${formatInlineMarkdown(
                    bulletMatch[1]
                )}</li>`;

                continue;
            }


            // -------------------------------------------------
            // NUMBERED LIST
            // -------------------------------------------------

            const numberedMatch = line.match(/^\d+\.\s+(.+)$/);

            if (numberedMatch) {
                if (paragraphBuffer.length > 0) {
                    addParagraph(paragraphBuffer);
                    paragraphBuffer = [];
                }

                if (inBulletList) {
                    html += "</ul>";
                    inBulletList = false;
                }

                if (!inNumberedList) {
                    html += "<ol>";
                    inNumberedList = true;
                }

                html += `<li>${formatInlineMarkdown(
                    numberedMatch[1]
                )}</li>`;

                continue;
            }


            // -------------------------------------------------
            // NORMAL TEXT
            // -------------------------------------------------

            closeLists();

            paragraphBuffer.push(line);
        }


        closeLists();

        if (paragraphBuffer.length > 0) {
            addParagraph(paragraphBuffer);
        }

        return html;
    }


    // =========================================================
    // RENDER CHAT
    // =========================================================

    function renderMessages() {
        chatMessages.replaceChildren();

        for (const message of messages) {
            const msgDiv = document.createElement("div");

            msgDiv.className =
                `message ${
                    message.role === "user"
                        ? "user-msg"
                        : "bot-msg"
                }`;

            if (message.role === "assistant") {
                // Render bot Markdown properly.
                msgDiv.innerHTML = renderMarkdown(
                    message.content
                );
            } else {
                // User messages should remain plain text.
                msgDiv.textContent = message.content;
            }

            chatMessages.appendChild(msgDiv);
        }

        chatMessages.scrollTop =
            chatMessages.scrollHeight;
    }


    // =========================================================
    // MESSAGE STORAGE
    // =========================================================

    function appendMessage(content, role) {
        messages.push({
            role,
            content
        });

        sessionStorage.setItem(
            historyKey,
            JSON.stringify(messages)
        );

        renderMessages();
    }


    function loadMessages() {
        try {
            const saved = JSON.parse(
                sessionStorage.getItem(historyKey) || "[]"
            );

            if (
                Array.isArray(saved) &&
                saved.every(
                    message =>
                        message.role &&
                        message.content
                )
            ) {
                return saved;
            }
        } catch (error) {
            console.warn(
                "Could not load saved chat history:",
                error
            );

            sessionStorage.removeItem(historyKey);
        }

        return [
            {
                role: "assistant",
                content:
                    "Hi! I am the SETTribe AI Assistant. " +
                    "I can help with courses, internships, fees and careers. " +
                    "What would you like to know?"
            }
        ];
    }


    // =========================================================
    // SESSION ID
    // =========================================================

    function getSessionId() {
        let id = sessionStorage.getItem(
            "settribe_session_id"
        );

        if (!id) {
            id = crypto.randomUUID();

            sessionStorage.setItem(
                "settribe_session_id",
                id
            );
        }

        return id;
    }


    // =========================================================
    // TYPING INDICATOR
    // =========================================================

    function showTypingIndicator() {
        removeTypingIndicator();

        const msgDiv =
            document.createElement("div");

        msgDiv.id = "typing-indicator";

        msgDiv.className =
            "message bot-msg typing-indicator";

        msgDiv.innerHTML =
            '<span class="typing-text">SETTribe AI Assistant is typing</span>' +
            '<span class="typing-dots">' +
            '<span>.</span><span>.</span><span>.</span>' +
            "</span>";

        chatMessages.appendChild(msgDiv);

        chatMessages.scrollTop =
            chatMessages.scrollHeight;
    }


    function removeTypingIndicator() {
        document
            .getElementById("typing-indicator")
            ?.remove();
    }


    // =========================================================
    // SEND MESSAGE
    // =========================================================

    async function sendMessage(event) {
        event.preventDefault();

        const text =
            userInput.value.trim();

        if (!text || sendBtn.disabled) {
            return;
        }

        appendMessage(
            text,
            "user"
        );

        userInput.value = "";

        sendBtn.disabled = true;

        userInput.disabled = true;

        showTypingIndicator();

        try {
            const response = await fetch(
                apiUrl,
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        session_id:
                            sessionId,
                        message: text
                    })
                }
            );

            let data;

            try {
                data = await response.json();
            } catch (jsonError) {
                throw new Error(
                    "The server returned an invalid response."
                );
            }

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "The chat request failed."
                );
            }

            const answer =
                data.answer ||
                "I could not generate a response.";

            removeTypingIndicator();

            appendMessage(
                answer,
                "assistant"
            );

        } catch (error) {
            console.error(
                "SETTribe chatbot error:",
                error
            );

            removeTypingIndicator();

            appendMessage(
                "Unable to reach the chatbot. " +
                "Please make sure the SETTribe backend is running.",
                "assistant"
            );

        } finally {
            sendBtn.disabled = false;

            userInput.disabled = false;

            userInput.focus();
        }
    }


    // =========================================================
    // CLEAR CHAT
    // =========================================================

    function clearChat() {
        messages = [];

        sessionStorage.removeItem(
            historyKey
        );

        messages.push({
            role: "assistant",
            content:
                "Hi! I am the SETTribe AI Assistant. " +
                "I can help with courses, internships, fees and careers. " +
                "What would you like to know?"
        });

        sessionStorage.setItem(
            historyKey,
            JSON.stringify(messages)
        );

        renderMessages();

        userInput.focus();
    }


    // =========================================================
    // EVENT LISTENERS
    // =========================================================

    renderMessages();

    chatForm.addEventListener(
        "submit",
        sendMessage
    );

    clearChatBtn.addEventListener(
        "click",
        clearChat
    );
});
