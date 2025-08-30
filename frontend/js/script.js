// API base URL - change this to your backend URL
const API_BASE_URL = 'http://localhost:5000';

// Global data store
let matchesData = [];
let valueBets = [];

// DOM elements
const matchesContainer = document.getElementById('matches-container');
const valueBetsContainer = document.getElementById('value-bets-container');
const performanceStats = document.getElementById('performance-stats');
const lastUpdatedElement = document.getElementById('last-updated');
const leagueFilter = document.getElementById('league-filter');
const helperStatusList = document.getElementById('helper-status');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    setupEventListeners();
    
    // Set up periodic data refresh (every 5 minutes)
    setInterval(loadData, 5 * 60 * 1000);
});

function setupEventListeners() {
    // League filter change
    leagueFilter.addEventListener('change', filterMatches);
    
    // Place bet button
    document.getElementById('place-bet-btn').addEventListener('click', placeBet);
}

function loadData() {
    fetchTodayMatches();
    updateHelperStatus();
}

function fetchTodayMatches() {
    showLoadingState();
    
    fetch(`${API_BASE_URL}/api/today-matches`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                matchesData = data.data;
                lastUpdatedElement.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
                renderMatches(matchesData);
                extractValueBets(matchesData);
            } else {
                showError('Failed to load matches data');
            }
        })
        .catch(error => {
            console.error('Error fetching matches:', error);
            showError('Failed to load matches. Please try again later.');
        });
}

function renderMatches(matches) {
    matchesContainer.innerHTML = '';
    
    if (matches.length === 0) {
        matchesContainer.innerHTML = '<div class="no-matches">No matches found for today</div>';
        return;
    }
    
    matches.forEach(match => {
        const prediction = match.prediction;
        const odds = match.odds_comparison;
        
        const matchElement = document.createElement('div');
        matchElement.className = 'match-card';
        matchElement.innerHTML = `
            <div class="match-header">
                <div class="league">
                    <i class="fas fa-trophy"></i>
                    <span>${match.league} • ${match.country}</span>
                </div>
                <div class="match-time">Today, ${match.time}</div>
            </div>
            <div class="teams">
                <div class="team">
                    <i class="fas fa-shield-alt fa-2x"></i>
                    <div class="team-name">${match.home_team}</div>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <i class="fas fa-shield-alt fa-2x"></i>
                    <div class="team-name">${match.away_team}</div>
                </div>
            </div>
            <div class="prediction">
                <div class="prediction-title">AI PREDICTION</div>
                <div class="prediction-details">
                    <div class="prediction-item">
                        <div class="prediction-value">${formatResult(prediction.predicted_result)}</div>
                        <div class="prediction-label">Result</div>
                    </div>
                    <div class="prediction-item">
                        <div class="prediction-value">${getBTTSPrediction(prediction)}</div>
                        <div class="prediction-label">BTTS</div>
                    </div>
                    <div class="prediction-item">
                        <div class="prediction-value">${getOverUnderPrediction(prediction)}</div>
                        <div class="prediction-label">Goals</div>
                    </div>
                </div>
                <div class="confidence">
                    <i class="fas fa-chart-line"></i>
                    <span>Confidence: ${Math.round(prediction.confidence * 100)}%</span>
                    <div class="confidence-bar">
                        <div class="confidence-level" style="width: ${prediction.confidence * 100}%;"></div>
                    </div>
                </div>
            </div>
            <div class="match-analysis">
                <div class="analysis-title">Key Factors:</div>
                <p>${generateKeyFactors(prediction)}</p>
                <div class="factors">
                    <span class="factor">Form</span>
                    <span class="factor">Injuries</span>
                    <span class="factor">Home Advantage</span>
                </div>
            </div>
            <div class="odds-comparison">
                <div class="odds-title">Best Odds:</div>
                <div class="odds-grid">
                    <div class="odds-source">
                        <span class="source-name">Hollywoodbets</span>
                        <span class="odds-value">${odds.hollywoodbets.home_win}</span>
                        <span class="odds-value">${odds.hollywoodbets.draw}</span>
                        <span class="odds-value">${odds.hollywoodbets.away_win}</span>
                    </div>
                    <div class="odds-source">
                        <span class="source-name">Betway</span>
                        <span class="odds-value">${odds.betway.home_win}</span>
                        <span class="odds-value">${odds.betway.draw}</span>
                        <span class="odds-value">${odds.betway.away_win}</span>
                    </div>
                </div>
            </div>
        `;
        
        matchesContainer.appendChild(matchElement);
    });
}

function extractValueBets(matches) {
    valueBets = [];
    valueBetsContainer.innerHTML = '';
    
    matches.forEach(match => {
        const prediction = match.prediction;
        const odds = match.odds_comparison;
        
        // Calculate value for home win
        const homeImpliedProb = 1 / odds.hollywoodbets.home_win;
        const homeValue = prediction.home_win_prob - homeImpliedProb;
        
        if (homeValue > 0.05) { // Threshold for value bet
            valueBets.push({
                type: 'home_win',
                match: `${match.home_team} vs ${match.away_team}`,
                odds: odds.hollywoodbets.home_win,
                value: homeValue,
                probability: prediction.home_win_prob
            });
        }
        
        // Similar calculations for draw and away win
        // ...
    });
    
    renderValueBets();
}

function renderValueBets() {
    valueBetsContainer.innerHTML = '';
    
    if (valueBets.length === 0) {
        valueBetsContainer.innerHTML = '<div class="no-value-bets">No strong value bets identified today</div>';
        return;
    }
    
    valueBets.slice(0, 4).forEach(bet => {
        const betElement = document.createElement('div');
        betElement.className = 'bet-option';
        betElement.innerHTML = `
            <div class="bet-name">${bet.match} - ${formatResult(bet.type)}</div>
            <div class="bet-odds">${bet.odds.toFixed(2)}</div>
            <div class="bet-confidence">Value: ${(bet.value * 100).toFixed(1)}%</div>
        `;
        
        valueBetsContainer.appendChild(betElement);
    });
}

function updateHelperStatus() {
    const helpers = [
        { name: 'Data Collector', status: 'working' },
        { name: 'Performance Analyzer', status: 'working' },
        { name: 'Form Calculator', status: 'working' },
        { name: 'Weather Analyst', status: 'idle' },
        { name: 'Injury Monitor', status: 'working' },
        { name: 'Transfer Impact', status: 'idle' },
        { name: 'Odds Analyzer', status: 'working' }
    ];
    
    helperStatusList.innerHTML = '';
    
    helpers.forEach(helper => {
        const helperElement = document.createElement('li');
        helperElement.className = 'helper-item';
        helperElement.innerHTML = `
            <div class="helper-icon"><i class="fas fa-${getHelperIcon(helper.name)}"></i></div>
            <div class="helper-name">${helper.name}</div>
            <div class="helper-status ${helper.status}"></div>
        `;
        
        helperStatusList.appendChild(helperElement);
    });
}

// Utility functions
function formatResult(result) {
    const resultMap = {
        'home_win': 'Home Win',
        'draw': 'Draw',
        'away_win': 'Away Win'
    };
    return resultMap[result] || result;
}

function getHelperIcon(helperName) {
    const iconMap = {
        'Data Collector': 'database',
        'Performance Analyzer': 'chart-line',
        'Form Calculator': 'bolt',
        'Weather Analyst': 'cloud-sun-rain',
        'Injury Monitor': 'user-injured',
        'Transfer Impact': 'people-arrows',
        'Odds Analyzer': 'balance-scale'
    };
    return iconMap[helperName] || 'cog';
}

function getBTTSPrediction(prediction) {
    // Simple heuristic for BTTS prediction
    const attackingStrength = (prediction.home_win_prob + prediction.away_win_prob) / 2;
    return attackingStrength > 0.6 ? 'Yes' : 'No';
}

function getOverUnderPrediction(prediction) {
    // Simple heuristic for over/under prediction
    const goalExpectancy = (prediction.home_win_prob + prediction.away_win_prob) * 1.5;
    return goalExpectancy > 1.5 ? '+2.5' : '-2.5';
}

function generateKeyFactors(prediction) {
    const factors = [];
    
    if (prediction.home_win_prob > 0.5) {
        factors.push('Strong home advantage');
    }
    
    if (prediction.confidence > 0.7) {
        factors.push('High prediction confidence');
    } else {
        factors.push('Uncertain match outcome');
    }
    
    if (prediction.home_win_prob + prediction.away_win_prob > 1.2) {
        factors.push('Expected goals from both sides');
    }
    
    return factors.join(', ');
}

function filterMatches() {
    const league = leagueFilter.value;
    
    if (league === 'all') {
        renderMatches(matchesData);
    } else {
        const filteredMatches = matchesData.filter(match => match.league === league);
        renderMatches(filteredMatches);
    }
}

function placeBet() {
    alert('This would open a betting slip with selected value bets. In a real implementation, this would connect to your betting account.');
}

function showLoadingState() {
    matchesContainer.innerHTML = '<div class="loading">Loading today\'s matches...</div>';
}

function showError(message) {
    matchesContainer.innerHTML = `<div class="error">${message}</div>`;
}
