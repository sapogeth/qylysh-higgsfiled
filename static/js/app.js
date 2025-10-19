// Aldar Köse Storyboard Generator - Frontend Logic

// DOM Elements
const promptInput = document.getElementById('promptInput');
const generateBtn = document.getElementById('generateBtn');
const errorMessage = document.getElementById('errorMessage');
const loadingOverlay = document.getElementById('loadingOverlay');
const outputSection = document.getElementById('outputSection');
const storyText = document.getElementById('storyText');
const framesContainer = document.getElementById('framesContainer');
const downloadBtn = document.getElementById('downloadBtn');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');
const newStoryBtn = document.getElementById('newStoryBtn');

// State
let currentStoryboard = null;

// Event Listeners
generateBtn.addEventListener('click', generateStoryboardStream);
newStoryBtn.addEventListener('click', resetForm);
downloadBtn.addEventListener('click', downloadAllImages);
downloadPdfBtn.addEventListener('click', downloadPDF);

// Allow Enter key to submit (with Shift+Enter for new line)
promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        generateStoryboardStream();
    }
});

// Suggestion cards click handlers
document.addEventListener('DOMContentLoaded', () => {
    const suggestionCards = document.querySelectorAll('.suggestion-card');

    suggestionCards.forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.getAttribute('data-prompt');
            promptInput.value = prompt;

            // Add visual feedback
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {
                card.style.transform = '';
            }, 150);

            // Scroll to textarea
            promptInput.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // Focus on textarea
            setTimeout(() => {
                promptInput.focus();
                // Move cursor to end
                promptInput.setSelectionRange(prompt.length, prompt.length);
            }, 300);
        });

        // Add hover effect for better UX
        card.addEventListener('mouseenter', () => {
            card.style.cursor = 'pointer';
        });
    });
});

// Streaming generation: render frames as they arrive
async function generateStoryboardStream() {
    const prompt = promptInput.value.trim();

    // Validation
    if (!prompt) {
        showError('Please enter a story idea!');
        return;
    }

    if (prompt.length < 10) {
        showError('Please provide a more detailed story idea (at least 10 characters).');
        return;
    }

    // Hide error and show loading
    hideError();
    showLoading();
    disableButton(generateBtn);

    try {
    // Prepare UI for streaming
    outputSection.style.display = 'block';
    framesContainer.innerHTML = '';
    storyText.innerHTML = '';

        // Start streaming from server
        const payload = { prompt };

        const response = await fetch('/api/generate/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok || !response.body) {
            throw new Error('Failed to start streaming generation');
        }

        // Pre-render a few skeleton cards while we wait for first events
        const skeletons = [];
        const SKELETON_COUNT = 6; // initial guess; we will trim/replace as real frames arrive
        for (let i = 0; i < SKELETON_COUNT; i++) {
            const sk = createSkeletonCard(i + 1);
            skeletons.push(sk);
            framesContainer.appendChild(sk);
        }

        // Read NDJSON chunks
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        const frames = [];

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });

            // Process complete lines
            let newlineIndex;
            while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
                const line = buffer.slice(0, newlineIndex).trim();
                buffer = buffer.slice(newlineIndex + 1);
                if (!line) continue;

                let event;
                try { event = JSON.parse(line); } catch { continue; }

                if (event.type === 'story') {
                    storyText.innerHTML = `
                        <strong>Aldar Köse Story:</strong><br>
                        ${escapeHtml(event.aldar_story)}
                    `;
                    // If we rendered too many skeletons, trim to total_frames
                    const total = Math.max(0, Number(event.total_frames || SKELETON_COUNT));
                    while (framesContainer.children.length > total) {
                        framesContainer.removeChild(framesContainer.lastChild);
                    }
                } else if (event.type === 'frame') {
                    const idx = event.index;
                    const frame = event.frame;
                    frames.push(frame);

                    // If there is a skeleton at this index, replace it; else append
                    const frameNum = frame.frame_number || (idx + 1);
                    const card = createFrameCard(frame, frameNum);
                    if (idx < framesContainer.children.length) {
                        framesContainer.replaceChild(card, framesContainer.children[idx]);
                    } else {
                        framesContainer.appendChild(card);
                    }
                    // Scroll as new frames appear
                    card.scrollIntoView({ behavior: 'smooth', block: 'end' });
                } else if (event.type === 'error') {
                    throw new Error(event.message || 'Generation error');
                } else if (event.type === 'complete') {
                    currentStoryboard = { storyboard: frames, metadata: { aldar_story: storyText.textContent } };
                    // Remove any remaining skeletons at the end
                    const realCount = frames.length;
                    while (framesContainer.children.length > realCount) {
                        framesContainer.removeChild(framesContainer.lastChild);
                    }
                }
            }
        }

    } catch (error) {
        console.error('Generation error:', error);
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
        enableButton(generateBtn);
    }
}

// Create a skeleton placeholder card
function createSkeletonCard(frameNumber) {
    const card = document.createElement('div');
    card.className = 'frame-card skeleton-card';
    card.innerHTML = `
        <div class="skeleton-image skeleton-shimmer"></div>
        <div class="frame-content">
            <span class="frame-number">Frame ${frameNumber}</span>
            <div class="skeleton-line wide skeleton-shimmer"></div>
            <div class="skeleton-line mid skeleton-shimmer"></div>
            <div class="skeleton-line short skeleton-shimmer"></div>
        </div>
    `;
    return card;
}

// Display the generated storyboard
function displayStoryboard(data) {
    const { storyboard, metadata } = data;

    // Show Aldar Köse story
    storyText.innerHTML = `
        <strong>Aldar Köse Story:</strong><br>
        ${escapeHtml(metadata.aldar_story)}
    `;

    // Clear previous frames
    framesContainer.innerHTML = '';

    // Create frame cards
    storyboard.forEach((frame, index) => {
        const frameCard = createFrameCard(frame, index + 1);
        framesContainer.appendChild(frameCard);
    });

    // Show output section
    outputSection.style.display = 'block';

    // Smooth scroll to output
    setTimeout(() => {
        outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Create a single frame card
function createFrameCard(frame, frameNumber) {
    const card = document.createElement('div');
    card.className = 'frame-card';

    const keyObjectsHtml = frame.key_objects
        ? frame.key_objects.map(obj => `<span class="meta-tag">${escapeHtml(obj)}</span>`).join('')
        : '';

    card.innerHTML = `
        <img
            src="${escapeHtml(frame.image_url)}"
            alt="Frame ${frameNumber}"
            class="frame-image"
            loading="lazy"
        >
        <div class="frame-content">
            <span class="frame-number">Frame ${frameNumber}</span>

            <div class="frame-rhyme">"${escapeHtml(frame.rhyme)}"</div>

            <div class="frame-description">
                ${escapeHtml(frame.description)}
            </div>

            <div class="frame-meta">
                <span class="meta-tag moral">💡 ${escapeHtml(frame.moral)}</span>
                <span class="meta-tag shot">🎬 ${escapeHtml(frame.shot_type)}</span>
            </div>

            ${frame.setting ? `<div class="frame-meta" style="margin-top: 8px;">
                <span class="meta-tag">📍 ${escapeHtml(frame.setting)}</span>
            </div>` : ''}

            ${keyObjectsHtml ? `<div class="frame-meta" style="margin-top: 8px;">
                ${keyObjectsHtml}
            </div>` : ''}
        </div>
    `;

    return card;
}

// Download all images
async function downloadPDF() {
    if (!currentStoryboard || !currentStoryboard.storyboard) {
        showError('No storyboard to download');
        return;
    }

    showLoading();
    updateLoadingText('Создание PDF в стиле визуальной новеллы...');

    try {
        // Prepare storyboard data with absolute image paths
        const storyboardData = {
            storyboard: currentStoryboard.storyboard.map(frame => ({
                ...frame,
                // Convert image_url to absolute path for PDF generator
                image_path: frame.image_url ? frame.image_url.replace('/static/generated/', 'static/generated/') : null
            })),
            metadata: currentStoryboard.metadata || {}
        };

        // Send to backend for PDF generation
        const response = await fetch('/api/export/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(storyboardData)
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.error || 'PDF generation failed');
        }

        // Download the PDF
        const pdfUrl = result.pdf_url;
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = result.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Success message
        alert('✅ PDF создан успешно! Проверьте папку загрузок.');

    } catch (error) {
        console.error('PDF download error:', error);
        showError(`Failed to generate PDF: ${error.message}`);
    } finally {
        hideLoading();
    }
}

async function downloadAllImages() {
    if (!currentStoryboard || !currentStoryboard.storyboard) {
        showError('No storyboard to download');
        return;
    }

    showLoading();

    try {
        for (const frame of currentStoryboard.storyboard) {
            await downloadImage(frame.image_url, `frame_${frame.frame_number}.png`);
            await sleep(500); // Small delay between downloads
        }

        alert('All images downloaded successfully!');
    } catch (error) {
        console.error('Download error:', error);
        showError('Failed to download some images. Please try downloading them individually.');
    } finally {
        hideLoading();
    }
}

// Download a single image
async function downloadImage(url, filename) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error(`Failed to download ${filename}:`, error);
        throw error;
    }
}

// Reset form for new story
function resetForm() {
    promptInput.value = '';
    outputSection.style.display = 'none';
    framesContainer.innerHTML = '';
    currentStoryboard = null;
    hideError();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Focus on input
    setTimeout(() => promptInput.focus(), 300);
}

// UI Helper Functions
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';
}

function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function updateLoadingText(text) {
    const loadingText = loadingOverlay.querySelector('p');
    if (loadingText) {
        loadingText.textContent = text;
    }
}

function disableButton(button) {
    button.disabled = true;
    button.querySelector('.btn-text').style.display = 'none';
    button.querySelector('.btn-loading').style.display = 'inline';
}

function enableButton(button) {
    button.disabled = false;
    button.querySelector('.btn-text').style.display = 'inline';
    button.querySelector('.btn-loading').style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Initial focus
window.addEventListener('load', () => {
    promptInput.focus();
});
