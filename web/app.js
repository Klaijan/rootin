// static/js/app.js

// Global state
let currentRoutine = [];

// Get data passed from server
const { products, apiBase } = window.appData;

// Convert products array to lookup object for easier access
const productLookup = {};
products.forEach(product => {
    productLookup[product.product_id] = product;
});

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, setting up event listeners...');
    initializeApp();
});

function initializeApp() {
    // Helper function to safely add event listeners
    function addEventListenerSafe(id, event, handler) {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener(event, handler);
            console.log('Added listener to:', id);
        } else {
            console.error('Element not found:', id);
        }
    }
    
    // Tab switching
    addEventListenerSafe('tab-routine', 'click', function() {
        switchTab('routine', this);
    });
    
    addEventListenerSafe('tab-analyze', 'click', function() {
        switchTab('analyze', this);
    });
    
    addEventListenerSafe('tab-treatments', 'click', function() {
        switchTab('treatments', this);
    });
    
    // Routine management
    addEventListenerSafe('addProductBtn', 'click', addProduct);
    addEventListenerSafe('addIngredientsBtn', 'click', addCustomIngredients);
    addEventListenerSafe('clearRoutineBtn', 'click', clearRoutine);
    
    // Analysis
    addEventListenerSafe('analyzeInteractionsBtn', 'click', analyzeInteractions);
    addEventListenerSafe('calculateScoresBtn', 'click', calculateScores);
    addEventListenerSafe('analyzeTreatmentBtn', 'click', analyzeTreatment);
    
    // Enter key support
    addEventListenerSafe('customIngredients', 'keypress', function(e) {
        if (e.key === 'Enter') addCustomIngredients();
    });
    
    console.log('Event listeners set up successfully');
}

// Tab Management
function switchTab(tabName, tabButton) {
    console.log('Switching to tab:', tabName);
    
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    tabButton.classList.add('active');
}

// Routine Management
function addProduct() {
    const productSelect = document.getElementById('productSelect');
    const productId = parseInt(productSelect.value);
    
    if (!productId) {
        alert('Please select a product');
        return;
    }
    
    const product = productLookup[productId];
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
    productSelect.value = ''; // Reset dropdown
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
        return;
    }
    
    let html = '';
    currentRoutine.forEach((item, index) => {
        let ingredientsList = '';
        
        // Show ingredients if it's a product
        if (item.item_type === 'product' && productLookup[item.product_id]) {
            const product = productLookup[item.product_id];
            if (product.inci_ingredients && product.inci_ingredients.length > 0) {
                const displayIngredients = product.inci_ingredients.slice(0, 4);
                ingredientsList = `<div style="margin-top: 8px; font-size: 12px; color: #666;">
                    <strong>Key ingredients:</strong> ${displayIngredients.join(', ')}${product.inci_ingredients.length > 4 ? '...' : ''}
                </div>`;
            }
        }
        
        html += `
            <div class="routine-item">
                <div class="routine-item-text">
                    <div style="font-weight: 600; color: #936964;">${item.label}</div>
                    ${ingredientsList}
                </div>
                <button class="btn btn-small" onclick="removeItem(${index})" style="background: #dc3545;">Remove</button>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function removeItem(index) {
    currentRoutine.splice(index, 1);
    updateRoutineDisplay();
}

function clearRoutine() {
    currentRoutine = [];
    updateRoutineDisplay();
    
    // Clear analysis results too
    document.getElementById('analysisResults').innerHTML = '';
    document.getElementById('treatmentResults').innerHTML = '';
}

// Analysis Functions
async function analyzeInteractions() {
    if (currentRoutine.length === 0) {
        alert('Please add items to your routine first');
        return;
    }
    
    const resultsDiv = document.getElementById('analysisResults');
    resultsDiv.innerHTML = '<div class="loading">🔍 Analyzing interactions...</div>';
    
    try {
        const response = await fetch(`${apiBase}/analyze/interactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: 'My Routine',
                items: currentRoutine,
                time_of_day: 'morning'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const interactions = await response.json();
        displayInteractions(interactions);
    } catch (error) {
        console.error('Analysis error:', error);
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
    if (currentRoutine.length === 0) {
        alert('Please add items to your routine first');
        return;
    }
    
    const resultsDiv = document.getElementById('analysisResults');
    resultsDiv.innerHTML = '<div class="loading">📊 Calculating scores...</div>';
    
    try {
        const response = await fetch(`${apiBase}/analyze/score`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: 'My Routine',
                items: currentRoutine,
                time_of_day: 'morning'
            })
        });
        
        if (!response.ok) {
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
    
    // Create container for chart
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
    
    // Create the spider chart
    setTimeout(() => {
        createSpiderChart(scores);
    }, 100); // Small delay to ensure canvas is rendered
}

function createSpiderChart(scores) {
    const ctx = document.getElementById('scoresChart');
    if (!ctx) {
        console.error('Canvas element not found');
        return;
    }
    
    const context = ctx.getContext('2d');
    
    // Prepare data for spider chart
    const categories = Object.keys(scores.category_scores);
    const values = Object.values(scores.category_scores);
    
    // Shorten labels for better fit on mobile
    const shortLabels = categories.map(label => {
        if (label.includes('&')) {
            return label.split(' &')[0]; // Take first part before &
        }
        return label.length > 15 ? label.substring(0, 12) + '...' : label;
    });
    
    new Chart(context, {
        type: 'radar',
        data: {
            labels: shortLabels,
            datasets: [{
                label: 'Routine Score',
                data: values,
                fill: true,
                backgroundColor: 'rgba(197, 208, 185, 0.2)', // sage with transparency
                borderColor: '#C5D0B9', // sage
                borderWidth: 2,
                pointBackgroundColor: '#C5D0B9', // sage
                pointBorderColor: '#936964', // font color
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // Hide legend to save space
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: Math.max(5, Math.max(...values) + 1), // Dynamic max based on data
                    ticks: {
                        display: false, // Hide tick numbers for cleaner look
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(197, 208, 185, 0.3)' // sage grid lines
                    },
                    angleLines: {
                        color: 'rgba(197, 208, 185, 0.3)' // sage angle lines
                    },
                    pointLabels: {
                        font: {
                            size: 11,
                            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                        },
                        color: '#936964' // font color
                    }
                }
            },
            interaction: {
                intersect: false
            },
            elements: {
                line: {
                    tension: 0.1
                }
            }
        }
    });
}

async function analyzeTreatment() {
    if (currentRoutine.length === 0) {
        alert('Please add items to your routine first');
        return;
    }
    
    const treatmentId = document.getElementById('treatmentSelect').value;
    const resultsDiv = document.getElementById('treatmentResults');
    
    resultsDiv.innerHTML = '<div class="loading">🏥 Analyzing post-treatment safety...</div>';
    
    try {
        const response = await fetch(`${apiBase}/analyze/post-treatment?treatment_id=${treatmentId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: 'My Routine',
                items: currentRoutine,
                time_of_day: 'morning'
            })
        });
        
        if (!response.ok) {
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
    
    let html = `<h4>🏥 Post-${result.treatment_name} Analysis:</h4>`;
    
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