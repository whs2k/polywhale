// main.js - Logic for Dashboard

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatAddress = (addr) => `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;

async function loadDashboard() {
    try {
        const response = await fetch('/api/whales');
        const data = await response.json();

        // Populate Stats
        document.getElementById('stat-total-profit').textContent = formatCurrency(data.stats.totalProfit);
        document.getElementById('stat-active-whales').textContent = data.stats.activeWhales;
        document.getElementById('stat-win-rate').textContent = data.stats.avgWinRate.toFixed(1) + '%';

        // Populate Table
        const tableBody = document.getElementById('whale-table-body');
        tableBody.innerHTML = '';

        data.whales.forEach(whale => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="rank">#${whale.rank}</td>
                <td><span class="address">${formatAddress(whale.address)}</span></td>
                <td class="positive">${formatCurrency(whale.profit)}</td>
                <td>${whale.winRate.toFixed(1)}%</td>
                <td>${formatCurrency(whale.volume)}</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error("Failed to load dashboard data", err);
    }
}

document.addEventListener('DOMContentLoaded', loadDashboard);
