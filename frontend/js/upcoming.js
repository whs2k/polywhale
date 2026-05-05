// upcoming.js - Logic for Upcoming Bets

document.addEventListener('DOMContentLoaded', () => {
    const data = window.PolyWhaleData;
    if (!data) return;

    const container = document.getElementById('bets-container');

    data.upcomingBets.forEach((bet, index) => {
        const card = document.createElement('div');
        card.className = 'bet-card';
        card.style.animationDelay = \`\${0.1 * (index + 1)}s\`;
        
        // Add animation class explicitly to ensure staggered effect
        card.classList.add('animate-fade-in');

        const sideClass = bet.side.toLowerCase();
        
        card.innerHTML = `
            <div class="bet-market">${bet.market}</div>
            
            <div class="bet-meta">
                <div class="highlight">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                    ${bet.whaleOverlap} Whales
                </div>
                <div>${bet.confidence}% Conviction</div>
            </div>
            
            <div class="bet-action">
                <div class="side-badge ${sideClass}">${bet.side}</div>
                <div class="volume">${data.formatCurrency(bet.totalVolume)}</div>
            </div>
        `;
        
        container.appendChild(card);
    });
});
