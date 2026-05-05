// main.js - Logic for Dashboard

document.addEventListener('DOMContentLoaded', () => {
    const data = window.PolyWhaleData;
    if (!data) return;

    // Populate Stats
    document.getElementById('stat-total-profit').textContent = data.formatCurrency(data.stats.totalProfit);
    document.getElementById('stat-active-whales').textContent = data.stats.activeWhales;
    document.getElementById('stat-win-rate').textContent = data.stats.avgWinRate.toFixed(1) + '%';

    // Populate Table (only show top 50 for performance and visual simplicity)
    const tableBody = document.getElementById('whale-table-body');
    const topWhales = data.whales.slice(0, 50);

    topWhales.forEach(whale => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td class="rank">#${whale.rank}</td>
            <td><span class="address">${data.formatAddress(whale.address)}</span></td>
            <td class="positive">${data.formatCurrency(whale.profit)}</td>
            <td>${whale.winRate.toFixed(1)}%</td>
            <td>${data.formatCurrency(whale.volume)}</td>
        `;
        
        tableBody.appendChild(row);
    });
});
