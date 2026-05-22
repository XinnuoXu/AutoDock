let proteinSequence = '';
let selectedPositions = new Set();

// DOM Elements
const proteinNameInput = document.getElementById('proteinName');
const proteinSequenceInput = document.getElementById('proteinSequence');
const loadSequenceBtn = document.getElementById('loadSequenceBtn');
const selectionSection = document.getElementById('selectionSection');
const sequenceDisplay = document.getElementById('sequenceDisplay');
const selectedPositionsDiv = document.getElementById('selectedPositions');
const saveBtn = document.getElementById('saveBtn');
const resetBtn = document.getElementById('resetBtn');
const statusMessage = document.getElementById('statusMessage');
const statsCard = document.getElementById('statsCard');
const totalResidues = document.getElementById('totalResidues');
const selectedCount = document.getElementById('selectedCount');

// Debug: Check if elements are found
console.log('Button elements:', {
    loadSequenceBtn,
    saveBtn,
    resetBtn
});

// Event Listeners
if (loadSequenceBtn) {
    loadSequenceBtn.addEventListener('click', loadSequence);
    console.log('Load button event listener attached');
} else {
    console.error('Load button not found!');
}

if (saveBtn) {
    saveBtn.addEventListener('click', saveProteinData);
}

if (resetBtn) {
    resetBtn.addEventListener('click', resetSelection);
}

function loadSequence() {
    const name = proteinNameInput.value.trim();
    const sequence = proteinSequenceInput.value.trim().toUpperCase();

    if (!name) {
        showToast('Please enter a protein name', 'error');
        return;
    }

    if (!sequence) {
        showToast('Please enter a protein sequence', 'error');
        return;
    }

    // Validate sequence (only letters)
    if (!/^[A-Z]+$/.test(sequence)) {
        showToast('Invalid sequence. Please use only amino acid letters (A-Z)', 'error');
        return;
    }

    proteinSequence = sequence;
    selectedPositions.clear();
    renderSequence();
    showStats();
    selectionSection.style.display = 'block';
    statsCard.style.display = 'block';
    showToast('Sequence loaded successfully!', 'success');
}

function renderSequence() {
    sequenceDisplay.innerHTML = '';

    for (let i = 0; i < proteinSequence.length; i++) {
        const aminoAcid = document.createElement('span');
        aminoAcid.className = 'amino-acid';
        aminoAcid.textContent = proteinSequence[i];
        aminoAcid.dataset.position = i;
        aminoAcid.title = `Position ${i}: ${proteinSequence[i]}`;

        aminoAcid.addEventListener('click', () => togglePosition(i, aminoAcid));

        sequenceDisplay.appendChild(aminoAcid);
    }

    updateSelectedDisplay();
}

function togglePosition(position, element) {
    if (selectedPositions.has(position)) {
        selectedPositions.delete(position);
        element.classList.remove('selected');
    } else {
        selectedPositions.add(position);
        element.classList.add('selected');
    }

    updateSelectedDisplay();
    updateStats();
}

function updateSelectedDisplay() {
    selectedPositionsDiv.innerHTML = '';

    if (selectedPositions.size === 0) {
        const emptyState = document.createElement('span');
        emptyState.className = 'empty-state';
        emptyState.textContent = 'No positions selected';
        selectedPositionsDiv.appendChild(emptyState);
    } else {
        const sorted = Array.from(selectedPositions).sort((a, b) => a - b);
        sorted.forEach(pos => {
            const tag = document.createElement('span');
            tag.className = 'position-tag';
            tag.textContent = `${proteinSequence[pos]}${pos}`;
            selectedPositionsDiv.appendChild(tag);
        });
    }
}

function showStats() {
    totalResidues.textContent = proteinSequence.length;
    selectedCount.textContent = selectedPositions.size;
}

function updateStats() {
    selectedCount.textContent = selectedPositions.size;
}

function resetSelection() {
    selectedPositions.clear();
    const aminoAcids = document.querySelectorAll('.amino-acid');
    aminoAcids.forEach(aa => aa.classList.remove('selected'));
    updateSelectedDisplay();
    updateStats();
    showToast('Selection cleared', 'success');
}

async function saveProteinData() {
    const name = proteinNameInput.value.trim();

    if (!name) {
        showToast('Please enter a protein name', 'error');
        return;
    }

    if (!proteinSequence) {
        showToast('Please load a sequence first', 'error');
        return;
    }

    const data = {
        protein_name: name,
        original_protein: proteinSequence,
        replace_pos: Array.from(selectedPositions).sort((a, b) => a - b)
    };

    // Disable button during save
    saveBtn.disabled = true;
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="spinner"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" opacity="0.3"/><path d="M14 8a6 6 0 0 1-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>Saving...';

    try {
        const response = await fetch('/api/save_protein', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            showToast(`Saved to ${result.filename}`, 'success');
        } else {
            showToast(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    }
}

function showToast(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `toast ${type} show`;

    setTimeout(() => {
        statusMessage.classList.remove('show');
    }, 4000);
}

// Add CSS for spinner animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    .spinner {
        animation: spin 0.8s linear infinite;
    }
`;
document.head.appendChild(style);
