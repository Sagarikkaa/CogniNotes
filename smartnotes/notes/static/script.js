/**
 * Smart Notes AI — Frontend JavaScript
 * Handles all UI interactions, API calls, and dynamic updates.
 * Uses the Fetch API for AJAX requests (no page reloads).
 */

// ==================== DOM ELEMENTS ====================
const noteInput = document.getElementById('noteInput');
const questionInput = document.getElementById('questionInput');
const charCount = document.getElementById('charCount');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const agentStep = document.getElementById('agentStep');

const summaryCard = document.getElementById('summaryCard');
const summaryResult = document.getElementById('summaryResult');
const keywordsCard = document.getElementById('keywordsCard');
const keywordsResult = document.getElementById('keywordsResult');
const qaCard = document.getElementById('qaCard');
const qaResult = document.getElementById('qaResult');

const toastContainer = document.getElementById('toastContainer');

// ==================== CHARACTER COUNTER ====================
noteInput.addEventListener('input', () => {
    const len = noteInput.value.length;
    charCount.textContent = `${len.toLocaleString()} character${len !== 1 ? 's' : ''}`;
});

// ==================== MAIN ACTION HANDLER ====================
/**
 * Handles all button actions (summarize, keywords, qa).
 * Validates input, shows loading spinner, calls the API,
 * and updates the UI with results.
 *
 * @param {string} action - One of: 'summarize', 'keywords', 'qa'
 */
async function handleAction(action) {
    const text = noteInput.value.trim();
    const question = questionInput.value.trim();

    // ---- Input Validation ----
    if (!text) {
        showToast('Please paste or type some notes first.', 'error');
        noteInput.focus();
        return;
    }

    if (action === 'qa' && !question) {
        showToast('Please enter a question about your notes.', 'error');
        questionInput.focus();
        return;
    }

    // ---- Prepare request body ----
    const body = {
        text: text,
        action: action,
    };

    if (action === 'qa') {
        body.question = question;
    }

    // ---- Show loading state ----
    showLoading(action);
    disableButtons(true);

    try {
        // ---- Call the backend API ----
        const response = await fetch('/api/process/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        // ---- Handle the response ----
        if (data.status === 'success') {
            displayResult(action, data.result);
            showToast(getSuccessMessage(action), 'success');
        } else {
            showToast(data.result || 'Something went wrong.', 'error');
        }

    } catch (error) {
        console.error('API call failed:', error);
        showToast('Network error. Please check if the server is running.', 'error');
    } finally {
        hideLoading();
        disableButtons(false);
    }
}

// ==================== DISPLAY RESULTS ====================
/**
 * Renders the result in the appropriate card.
 *
 * @param {string} action - The action that produced this result
 * @param {*} result - The result data (string, array, or object)
 */
function displayResult(action, result) {
    if (action === 'summarize') {
        summaryResult.textContent = result;
        summaryCard.style.display = 'block';
        // Scroll into view smoothly
        summaryCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    } else if (action === 'keywords') {
        // Render keywords as styled tags
        if (Array.isArray(result)) {
            keywordsResult.innerHTML = result
                .map((kw, i) =>
                    `<span class="keyword-tag" style="animation-delay: ${i * 0.05}s">${escapeHtml(kw)}</span>`
                )
                .join('');
        } else {
            keywordsResult.textContent = result;
        }
        keywordsCard.style.display = 'block';
        keywordsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    } else if (action === 'qa') {
        if (typeof result === 'object' && result.answer) {
            // Build answer display with confidence badge
            let html = `<p>${escapeHtml(result.answer)}</p>`;

            if (result.confidence !== undefined) {
                const conf = result.confidence;
                const pct = (conf * 100).toFixed(1);
                let levelClass = 'confidence-low';
                let levelLabel = 'Low';

                if (conf >= 0.7) {
                    levelClass = 'confidence-high';
                    levelLabel = 'High';
                } else if (conf >= 0.3) {
                    levelClass = 'confidence-medium';
                    levelLabel = 'Medium';
                }

                html += `
                    <div class="confidence-badge ${levelClass}">
                        <span>🎯</span>
                        <span>Confidence: ${pct}% (${levelLabel})</span>
                    </div>
                `;
            }

            qaResult.innerHTML = html;
        } else {
            qaResult.textContent = result;
        }
        qaCard.style.display = 'block';
        qaCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// ==================== LOADING SPINNER ====================
/**
 * Shows the loading overlay with action-specific messages.
 * @param {string} action - The current action being performed
 */
function showLoading(action) {
    const messages = {
        summarize: {
            main: 'Generating summary...',
            step: 'Summarization Agent (BART) is processing your notes'
        },
        keywords: {
            main: 'Extracting keywords...',
            step: 'Keyword Agent (TF-IDF) is analyzing your text'
        },
        qa: {
            main: 'Finding answer...',
            step: 'Q&A Agent (DistilBERT) is searching your notes'
        }
    };

    const msg = messages[action] || { main: 'Processing...', step: 'Working...' };
    loadingText.textContent = msg.main;
    agentStep.querySelector('.step-label').textContent = msg.step;
    loadingOverlay.classList.add('active');
}

/**
 * Hides the loading overlay.
 */
function hideLoading() {
    loadingOverlay.classList.remove('active');
}

// ==================== BUTTON STATE ====================
/**
 * Enables or disables all action buttons.
 * @param {boolean} disabled - Whether to disable the buttons
 */
function disableButtons(disabled) {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.disabled = disabled;
    });
}

// ==================== TOAST NOTIFICATIONS ====================
/**
 * Shows a temporary toast notification.
 *
 * @param {string} message - The message to display
 * @param {string} type - 'error', 'success', or 'info'
 * @param {number} duration - How long to show the toast (ms)
 */
function showToast(message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ==================== COPY TO CLIPBOARD ====================
/**
 * Copies the text content of an element to the clipboard.
 * @param {string} elementId - The ID of the element to copy from
 */
function copyToClipboard(elementId) {
    const el = document.getElementById(elementId);
    const text = el.textContent || el.innerText;

    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success', 2000);
    }).catch(() => {
        showToast('Failed to copy.', 'error');
    });
}

// ==================== HELPER FUNCTIONS ====================
/**
 * Escapes HTML special characters to prevent XSS.
 * @param {string} text - Raw text to escape
 * @returns {string} HTML-safe text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Returns a success toast message for the given action.
 * @param {string} action - The completed action
 * @returns {string} A user-friendly success message
 */
function getSuccessMessage(action) {
    const messages = {
        summarize: '✨ Summary generated successfully!',
        keywords: '🔑 Keywords extracted successfully!',
        qa: '💡 Answer found!'
    };
    return messages[action] || 'Done!';
}
