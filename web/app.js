// web/app.js

// Configuration
const API_BASE = window.appData?.apiBase || 'http://localhost:8000/api';

// Global state
let currentRoutine = [];
let savedRoutines = [];
let products = [];
let stepNames = {};


async function loadStepNames() {
    try {
        const response = await fetch(`${API_BASE}/config/step-names`);
        if (response.ok) {
            stepNames = await response.json();
            console.log('Step names loaded from CSV:', stepNames);
        } else {
            throw new Error('Failed to load step names from API');
        }
    } catch (error) {
        console.error('Error loading step names:', error);
        // Fallback to your CSV values
        stepNames = {
            1: "Cleanser",
            2: "Exfoliator",
            3: "Toner and Essence",
            5: "Treatment",
            6: "Sheet Mask",
            7: "Eye Care",
            8: "Moisturizer",
            9: "Face Oil",
            10: "Sun Protection",
            999: "Additional Care"
        };
    }
}

// Helper function to get step name
function getStepOrderName(stepOrder) {
    return stepNames[stepOrder] || stepNames[999] || "Additional Care";
}


// Initialize app when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🧴 Rootin app starting...');
    initializeApp();
});


async function initializeApp() {
    await checkAPIConnection();
    await loadProducts();
    await loadStepNames();
    await loadSavedRoutines();
    setupEventListeners();
}

async function checkAPIConnection() {
    const statusElement = document.getElementById('apiStatus');
    try {
        const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
        if (response.ok) {
            statusElement.textContent = '🟢 Connected to API';
            statusElement.className = 'api-status connected';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        statusElement.textContent = '🔴 API Disconnected';
        statusElement.className = 'api-status disconnected';
        console.error('API connection failed:', error);
    }
}


async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products`);
        if (response.ok) {
            products = await response.json();
            window.appData.products = products; // Store in window.appData
            populateProductDropdown();
        } else {
            console.error('Failed to load products');
            // Use fallback products
            products = [
                {product_id: 1, brand_name: "Kiehl's", product_name: "Micro-Dose Anti-Aging Retinol Serum"},
                {product_id: 2, brand_name: "The Ordinary", product_name: "Niacinamide 10% + Zinc 1%"},
                {product_id: 3, brand_name: "La Roche Posay", product_name: "Vitamin C12 Serum"}
            ];
            window.appData.products = products;
            populateProductDropdown();
        }
    } catch (error) {
        console.error('Error loading products:', error);
        products = [
            {product_id: 1, brand_name: "Kiehl's", product_name: "Micro-Dose Anti-Aging Retinol Serum"},
            {product_id: 2, brand_name: "The Ordinary", product_name: "Niacinamide 10% + Zinc 1%"},
            {product_id: 3, brand_name: "La Roche Posay", product_name: "Vitamin C12 Serum"}
        ];
        window.appData.products = products;
        populateProductDropdown();
    }
}

async function loadSavedRoutines() {
    try {
        const response = await fetch(`${API_BASE}/routines`);
        if (response.ok) {
            const data = await response.json();
            savedRoutines = data.routines || [];
        } else {
            console.error('Failed to load saved routines');
            savedRoutines = [];
        }
    } catch (error) {
        console.error('Error loading saved routines:', error);
        savedRoutines = [];
    }
    
    updateRoutineDropdowns();
    displaySavedRoutinesList();
}

function populateProductDropdown() {
    const select = document.getElementById('productSelect');
    select.innerHTML = '<option value="">Select a product...</option>';
    
    products.forEach(product => {
        const option = document.createElement('option');
        option.value = product.product_id;
        option.textContent = `${product.brand_name} - ${product.product_name}`;
        select.appendChild(option);
    });
}

function updateRoutineDropdowns() {
    const dropdowns = ['analyzeRoutineSelect', 'treatmentRoutineSelect', 'savedRoutineSelect'];
    
    dropdowns.forEach(dropdownId => {
        const select = document.getElementById(dropdownId);
        if (!select) return;
        
        select.innerHTML = '<option value="">Select a routine...</option>';
        
        if (Array.isArray(savedRoutines)) {
            savedRoutines.forEach(routine => {
                const option = document.createElement('option');
                option.value = routine.routine_id;
                option.textContent = routine.name;
                select.appendChild(option);
            });
        }
    });
}

function displaySavedRoutinesList() {
    const container = document.getElementById('routinesContainer');
    
    if (!container) return;
    
    if (!Array.isArray(savedRoutines) || savedRoutines.length === 0) {
        container.innerHTML = '<div class="empty-state">No saved routines yet. Create some routines first!</div>';
        return;
    }
    
    container.innerHTML = savedRoutines.map(routine => `
        <div class="routine-display" style="margin-bottom: 15px;">
            <h4 style="color: #936964; margin-bottom: 10px;">${routine.name}</h4>
            <p style="font-size: 14px; color: #666; margin-bottom: 10px;">
                Created: ${new Date(routine.created_at).toLocaleDateString()}
            </p>
            <button class="btn btn-small" onclick="deleteRoutine('${routine.routine_id}')" style="background: #dc3545; width: auto;">
                Delete
            </button>
        </div>
    `).join('');
}
function formatRoutineDisplay(routine) {
    if (!routine.items || routine.items.length === 0) {
        return `
            <div class="routine-display-container">
                <div class="routine-title">${routine.name}</div>
                <div class="empty-state">No products found in this routine</div>
            </div>
        `;
    }

    let html = `<div class="routine-display-container">`;
    html += `<div class="routine-title">${routine.name}</div>`;

    // Group products by routine_step_order for display
    const groupedByStep = {};
    
    routine.items.forEach(product => {
        // Use routine_step_order if available, otherwise fall back to grouping by step_order
        const stepNum = product.routine_step_order || product.step_order || 999;
        
        if (!groupedByStep[stepNum]) {
            groupedByStep[stepNum] = {
                step_number: stepNum,
                step_name: product.step_name || getStepOrderName(product.step_order),
                products: []
            };
        }
        groupedByStep[stepNum].products.push(product);
    });
    
    // Sort by step number (which is now sequential)
    const sortedSteps = Object.keys(groupedByStep)
        .sort((a, b) => parseInt(a) - parseInt(b))
        .map(key => groupedByStep[key]);
    
    // Display each step
    sortedSteps.forEach(step => {
        html += `<div class="routine-step-display">`;
        
        // Display the sequential step number
        html += `<div class="step-title">Step ${step.step_number}: ${step.step_name}</div>`;
        
        // List products in this step
        step.products.forEach(productInfo => {
            const brandName = productInfo.brand_name || 'Unknown Brand';
            const productName = productInfo.product_name || 'Unknown Product';
            
            let productText = `${brandName} - ${productName}`;
            
            if (productInfo.product_texture && productInfo.product_texture !== 'null') {
                productText += ` <span style="font-size: 12px; color: #999;">(${productInfo.product_texture})</span>`;
            }
            
            html += `<div class="step-product">${productText}</div>`;
        });
        
        html += `</div>`;
    });

    // Add summary
    const totalProducts = routine.items.length;
    const totalSteps = sortedSteps.length;
    html += `
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e0e0e0; text-align: center; color: #666; font-size: 14px;">
            ${totalSteps} step${totalSteps > 1 ? 's' : ''} • ${totalProducts} product${totalProducts > 1 ? 's' : ''}
        </div>
    `;

    html += `</div>`;
    return html;
}

async function displaySelectedRoutine() {
    const routineSelect = document.getElementById('savedRoutineSelect');
    const routineId = routineSelect.value;
    const displayArea = document.getElementById('routineDisplayArea');
    
    if (!routineId) {
        alert('Please select a routine to display');
        return;
    }
    
    displayArea.innerHTML = '<div class="loading">📱 Loading routine...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/routines/${routineId}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const routine = await response.json();
        
        // Debug log to verify structure
        console.log('Routine loaded:', {
            name: routine.name,
            itemCount: routine.items?.length,
            firstItem: routine.items?.[0]
        });
        
        displayArea.innerHTML = formatRoutineDisplay(routine);
        
    } catch (error) {
        console.error('Display routine error:', error);
        displayArea.innerHTML = `
            <div class="error">
                <strong>Error loading routine:</strong><br>
                ${error.message}
            </div>
        `;
    }
}

function setupEventListeners() {
    function addEventListenerSafe(id, event, handler) {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener(event, handler);
            console.log(`✅ Added ${event} listener to ${id}`);
        } else {
            console.error(`❌ Element not found: ${id}`);
        }
    }
    
    // Tab switching
    addEventListenerSafe('tab-product', 'click', function() { switchTab('product', this); });
    addEventListenerSafe('tab-routine', 'click', function() { switchTab('routine', this); });
    addEventListenerSafe('tab-analyze', 'click', function() { switchTab('analyze', this); });
    addEventListenerSafe('tab-treatments', 'click', function() { switchTab('treatments', this); });
    
    // Routine management
    addEventListenerSafe('addProductBtn', 'click', addProduct);
    addEventListenerSafe('addIngredientsBtn', 'click', addCustomIngredients);
    addEventListenerSafe('clearRoutineBtn', 'click', clearRoutine);
    
    // Create Routine functionality
    addEventListenerSafe('createRoutineBtn', 'click', showRoutineBuilder);
    addEventListenerSafe('saveRoutineBtn', 'click', saveRoutine);
    addEventListenerSafe('cancelRoutineBtn', 'click', hideRoutineBuilder);
    
    // Display routine
    addEventListenerSafe('displayRoutineBtn', 'click', displaySelectedRoutine);
    
    // Analysis
    addEventListenerSafe('analyzeInteractionsBtn', 'click', analyzeInteractions);
    addEventListenerSafe('calculateScoresBtn', 'click', calculateScores);
    addEventListenerSafe('analyzeTreatmentBtn', 'click', analyzeTreatment);
    
    // Enter key support
    addEventListenerSafe('customIngredients', 'keypress', function(e) {
        if (e.key === 'Enter') addCustomIngredients();
    });
    
    console.log('✅ Event listeners setup complete');
}

function switchTab(tabName, tabButton) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    tabButton.classList.add('active');
}

function addProduct() {
    const productSelect = document.getElementById('productSelect');
    const productId = parseInt(productSelect.value);
    
    if (!productId) {
        alert('Please select a product');
        return;
    }
    
    const product = products.find(p => p.product_id === productId);
    if (!product) {
        alert('Product not found');
        return;
    }
    
    const item = {
        item_type: 'product',
        product_id: productId,
        label: `${product.brand_name} - ${product.product_name}`
    };
    
    currentRoutine.push(item);
    updateRoutineDisplay();
    productSelect.value = '';
}

function addCustomIngredients() {
    const ingredients = document.getElementById('customIngredients').value.trim();
    
    if (!ingredients) {
        alert('Please enter ingredient names');
        return;
    }
    
    const ingredientList = ingredients.split(',').map(ing => ing.trim()).filter(ing => ing);
    const item = {
        item_type: 'custom',
        ingredient_names: ingredientList,
        label: `Custom: ${ingredientList.join(', ')}`
    };
    
    currentRoutine.push(item);
    updateRoutineDisplay();
    document.getElementById('customIngredients').value = '';
}

function updateRoutineDisplay() {
    const container = document.getElementById('routineItems');
    
    if (currentRoutine.length === 0) {
        container.innerHTML = '<div class="empty-state">No items in routine yet. Add products or ingredients above!</div>';
        updateCreateButtonVisibility();
        return;
    }
    
    let html = '';
    currentRoutine.forEach((item, index) => {
        html += `
            <div class="routine-item">
                <div class="routine-item-text">
                    <div style="font-weight: 600; color: #936964;">${item.label}</div>
                </div>
                <button class="btn btn-small" onclick="removeItem(${index})" style="background: #dc3545;">Remove</button>
            </div>
        `;
    });
    
    container.innerHTML = html;
    updateCreateButtonVisibility();
}

function updateCreateButtonVisibility() {
    const createBtn = document.getElementById('createRoutineBtn');
    if (currentRoutine.length > 0) {
        createBtn.style.display = 'block';
    } else {
        createBtn.style.display = 'none';
    }
}

// Make removeItem globally accessible
window.removeItem = function(index) {
    currentRoutine.splice(index, 1);
    updateRoutineDisplay();
}

function clearRoutine() {
    currentRoutine = [];
    updateRoutineDisplay();
    document.getElementById('analysisResults').innerHTML = '';
    document.getElementById('treatmentResults').innerHTML = '';
    hideRoutineBuilder();
}

function showRoutineBuilder() {
    if (currentRoutine.length === 0) {
        alert('Please add some products or ingredients to your routine first');
        return;
    }
    
    document.getElementById('routineBuilder').classList.add('active');
    document.getElementById('createRoutineBtn').style.display = 'none';
    updateCurrentItemsPreview();
    document.getElementById('routineName').value = '';
}

function updateCurrentItemsPreview() {
    const preview = document.getElementById('currentItemsPreview');
    
    if (currentRoutine.length === 0) {
        preview.innerHTML = '<div style="color: #666; font-style: italic;">No items in current routine</div>';
        return;
    }
    
    preview.innerHTML = currentRoutine.map((item, index) => `
        <div style="display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">
            <div style="background: #C5D0B9; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; margin-right: 10px;">
                ${index + 1}
            </div>
            <div style="flex: 1; font-size: 14px; color: #936964;">
                ${item.label}
            </div>
        </div>
    `).join('');
}

function hideRoutineBuilder() {
    document.getElementById('routineBuilder').classList.remove('active');
    updateCreateButtonVisibility();
}

async function saveRoutine() {
    const routineName = document.getElementById('routineName').value.trim();
    
    if (!routineName) {
        alert('Please enter a routine name');
        return;
    }
    
    // Extract only product IDs from products (not custom ingredients)
    const product_ids = currentRoutine
        .filter(item => item.item_type === 'product')
        .map(item => item.product_id);
    
    if (product_ids.length === 0) {
        alert('Please add at least one product to the routine');
        return;
    }
    
    // Create the request payload
    const requestPayload = {
        name: routineName,
        description: "",
        product_ids: product_ids,
        time_of_day: "morning",  // Make sure this is not null
        user_id: null
    };
    
    // Log what we're sending for debugging
    console.log('Sending routine data:', requestPayload);
    console.log('Product IDs being sent:', product_ids);
    
    try {
        const response = await fetch(`${API_BASE}/routines`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestPayload)
        });
        
        // Log the response status
        console.log('Response status:', response.status);
        
        // Try to get the response body
        const responseText = await response.text();
        console.log('Raw response:', responseText);
        
        let responseData;
        try {
            responseData = JSON.parse(responseText);
        } catch (e) {
            console.error('Failed to parse response as JSON:', e);
            throw new Error(`Server returned invalid JSON: ${responseText}`);
        }
        
        if (!response.ok) {
            // Log the full error details
            console.error('Error response:', responseData);
            
            // Handle validation errors specifically
            if (response.status === 422) {
                console.error('Validation error details:', responseData.detail);
                
                // Parse validation errors if they exist
                if (Array.isArray(responseData.detail)) {
                    const errors = responseData.detail.map(err => 
                        `${err.loc.join('.')}: ${err.msg}`
                    ).join('\n');
                    throw new Error(`Validation errors:\n${errors}`);
                } else {
                    throw new Error(responseData.detail || 'Validation error');
                }
            }
            
            throw new Error(responseData.detail || `HTTP ${response.status} error`);
        }
        
        const savedRoutine = responseData;
        console.log('Routine saved successfully:', savedRoutine);
        
        // Add to saved routines
        if (!Array.isArray(savedRoutines)) {
            savedRoutines = [];
        }
        savedRoutines.push(savedRoutine);
        
        // Update UI
        hideRoutineBuilder();
        updateRoutineDropdowns();
        displaySavedRoutinesList();
        
        // Clear current routine after successful save
        currentRoutine = [];
        updateRoutineDisplay();
        
        alert(`Routine "${savedRoutine.name}" saved successfully!`);
        
    } catch (error) {
        console.error("Full error details:", error);
        alert(`Failed to save routine: ${error.message}`);
    }
}

// Make deleteRoutine globally accessible
window.deleteRoutine = async function(routineId) {
    if (!confirm('Are you sure you want to delete this routine?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/routines/${routineId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            savedRoutines = savedRoutines.filter(r => r.routine_id !== routineId);
            updateRoutineDropdowns();
            displaySavedRoutinesList();
            alert('Routine deleted successfully!');
        } else {
            throw new Error('Failed to delete routine');
        }
    } catch (error) {
        console.error('Delete routine error:', error);
        alert('Failed to delete routine: ' + error.message);
    }
}

async function analyzeInteractions() {
    const routineSelect = document.getElementById('analyzeRoutineSelect');
    const routineId = routineSelect.value;
    
    if (!routineId) {
        alert('Please select a saved routine to analyze');
        return;
    }
    
    const resultsDiv = document.getElementById('analysisResults');
    resultsDiv.innerHTML = '<div class="loading">🔍 Analyzing interactions...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/routines/${routineId}/analyze/interactions`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const interactions = await response.json();
        displayInteractions(interactions);
    } catch (error) {
        console.error('Interaction analysis error:', error);
        resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}

function displayInteractions(interactions) {
    const resultsDiv = document.getElementById('analysisResults');
    
    if (interactions.length === 0) {
        resultsDiv.innerHTML = '<div class="success">✅ No problematic interactions found!</div>';
        return;
    }
    
    let html = '<h4>🔍 Ingredient Interactions Found:</h4>';
    interactions.forEach(interaction => {
        const typeClass = `interaction-${interaction.interaction_type.toLowerCase()}`;
        const emoji = interaction.interaction_type === 'clash' ? '⚠️' : 
                     interaction.interaction_type === 'caution' ? '🟡' : '✅';
        
        html += `
            <div class="interaction-item ${typeClass}">
                <strong>${emoji} ${interaction.interaction_type.toUpperCase()}</strong><br>
                <strong>${interaction.ingredient_a_name} × ${interaction.ingredient_b_name}</strong><br>
                <div style="font-size: 12px; color: #666; margin: 5px 0;">
                    From: ${interaction.product_a}<br>
                    And: ${interaction.product_b}
                </div>
                <strong>Effect:</strong> ${interaction.effect}<br>
                <strong>Details:</strong> ${interaction.details}
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

async function calculateScores() {
    const routineSelect = document.getElementById('analyzeRoutineSelect');
    const routineId = routineSelect.value;
    
    if (!routineId) {
        alert('Please select a saved routine to analyze');
        return;
    }
    
    const resultsDiv = document.getElementById('analysisResults');
    resultsDiv.innerHTML = '<div class="loading">📊 Calculating scores...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/routines/${routineId}/analyze/score`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const scores = await response.json();
        displayScores(scores);
    } catch (error) {
        console.error('Scoring error:', error);
        resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}

function displayScores(scores) {
    const resultsDiv = document.getElementById('analysisResults');
    
    let html = `
        <h4>📊 Your Routine Scores:</h4>
        <div class="chart-container">
            <canvas id="scoresChart" class="chart-canvas"></canvas>
        </div>
        <div class="score-card" style="margin-top: 15px;">
            <div class="score-value">${scores.total_score.toFixed(1)}</div>
            <div class="score-label">Total Routine Score</div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    setTimeout(() => createSpiderChart(scores), 100);
}

function createSpiderChart(scores) {
    const ctx = document.getElementById('scoresChart');
    if (!ctx) return;
    
    const categories = Object.keys(scores.category_scores);
    const values = Object.values(scores.category_scores);
    
    const shortLabels = categories.map(label => {
        if (label.includes('&')) {
            return label.split(' &')[0];
        }
        return label.length > 15 ? label.substring(0, 12) + '...' : label;
    });
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: shortLabels,
            datasets: [{
                label: 'Routine Score',
                data: values,
                fill: true,
                backgroundColor: 'rgba(197, 208, 185, 0.2)',
                borderColor: '#C5D0B9',
                borderWidth: 2,
                pointBackgroundColor: '#C5D0B9',
                pointBorderColor: '#936964',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                r: {
                    beginAtZero: true,
                    max: Math.max(5, Math.max(...values) + 1),
                    ticks: { display: false },
                    grid: { color: 'rgba(197, 208, 185, 0.3)' },
                    angleLines: { color: 'rgba(197, 208, 185, 0.3)' },
                    pointLabels: {
                        font: { size: 11 },
                        color: '#936964'
                    }
                }
            }
        }
    });
}

async function analyzeTreatment() {
    const routineSelect = document.getElementById('treatmentRoutineSelect');
    const routineId = routineSelect.value;
    const treatmentId = document.getElementById('treatmentSelect').value;
    
    if (!routineId) {
        alert('Please select a saved routine to analyze');
        return;
    }
    
    const resultsDiv = document.getElementById('treatmentResults');
    resultsDiv.innerHTML = '<div class="loading">🏥 Analyzing post-treatment safety...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/routines/${routineId}/analyze/post-treatment/${treatmentId}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displayTreatmentResults(result);
    } catch (error) {
        console.error('Treatment analysis error:', error);
        resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}

function displayTreatmentResults(result) {
    const resultsDiv = document.getElementById('treatmentResults');
    const displayName = result.display_name || result.treatment_name;
    
    let html = `<h4>🏥 Post-${displayName} Analysis:</h4>`;
    
    if (Object.keys(result.flagged_products).length === 0) {
        html += '<div class="success">✅ All products in your routine are safe to use after your treatment!</div>';
    } else {
        for (const [productName, warnings] of Object.entries(result.flagged_products)) {
            html += `<div class="interaction-item">
                <strong>📦 ${productName}</strong><br><br>`;
            
            warnings.forEach(warning => {
                const emoji = warning.action === 'avoid' ? '🚫' : '⚠️';
                const actionClass = warning.action === 'avoid' ? 'interaction-clash' : 'interaction-caution';
                
                html += `
                    <div class="${actionClass}" style="margin: 8px 0; padding: 10px; border-radius: 6px;">
                        <strong>${emoji} ${warning.action.toUpperCase()}:</strong> ${warning.ingredient}<br>
                        <strong>Reason:</strong> ${warning.reason}<br>
                        <strong>Duration:</strong> ${warning.duration_days} days
                    </div>
                `;
            });
            
            html += '</div>';
        }
    }
    
    resultsDiv.innerHTML = html;
}