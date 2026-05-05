// live.js - Logic for Live Feed

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatAddress = (addr) => `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;

async function fetchLiveTrades() {
    try {
        const response = await fetch('/api/live');
        const data = await response.json();
        
        const tableBody = document.getElementById('live-table-body');
        tableBody.innerHTML = ''; // Clear current

        data.trades.forEach(trade => {
            const row = document.createElement('tr');
            const sideClass = trade.side.toUpperCase() === 'BUY' ? 'positive' : 'text-muted';
            
            row.innerHTML = `
                <td>${trade.timestamp}</td>
                <td><span class="address">${formatAddress(trade.wallet_address)}</span></td>
                <td>${formatAddress(trade.market_id)}</td>
                <td class="${sideClass}">${trade.side}</td>
                <td>${trade.amount.toFixed(2)}</td>
                <td>${formatCurrency(trade.price)}</td>
                <td class="fee-cell">${formatCurrency((trade.amount * trade.price * trade.fee_bps) / 10000)}</td>
            `;
            
            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error("Failed to fetch live trades", err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchLiveTrades();
    // Poll every 5 seconds
    setInterval(fetchLiveTrades, 5000);
});
