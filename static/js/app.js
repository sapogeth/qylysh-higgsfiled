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
const newStoryBtn = document.getElementById('newStoryBtn');

// State
let currentStoryboard = null;

// Event Listeners
generateBtn.addEventListener('click', generateStoryboard);
newStoryBtn.addEventListener('click', resetForm);
downloadBtn.addEventListener('click', downloadAllImages);

// Allow Enter key to submit (with Shift+Enter for new line)
promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        generateStoryboard();
    }
});

// Main function to generate storyboard
async function generateStoryboard() {
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
        // Call API
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate storyboard');
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Generation failed');
        }

        // Store storyboard
        currentStoryboard = data;

        // Display results
        displayStoryboard(data);

    } catch (error) {
        console.error('Generation error:', error);
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
        enableButton(generateBtn);
    }
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
