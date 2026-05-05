// Mock Data generator for PolyWhale

const generateRandomAddress = () => {
  const chars = '0123456789abcdef';
  let addr = '0x';
  for (let i = 0; i < 40; i++) {
    addr += chars[Math.floor(Math.random() * chars.length)];
  }
  return addr;
};

const formatAddress = (addr) => {
  return `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;
};

const formatCurrency = (num) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(num);
};

// Generate top 500 whales
const generateWhales = () => {
  const whales = [];
  let currentProfit = 5000000; // Max profit
  
  for (let i = 1; i <= 500; i++) {
    const profit = currentProfit * (0.8 + (Math.random() * 0.4)); // Some variance
    const winRate = 50 + Math.random() * 45; // 50% to 95%
    const volume = profit * (2 + Math.random() * 5);
    
    whales.push({
      rank: i,
      address: generateRandomAddress(),
      profit: profit,
      winRate: winRate,
      volume: volume
    });
    
    // Decay profit for next rank
    currentProfit = currentProfit * 0.985;
  }
  
  return whales;
};

const WHALES = generateWhales();

const MOCK_STATS = {
  totalProfit: WHALES.reduce((sum, w) => sum + w.profit, 0),
  activeWhales: 500,
  avgWinRate: WHALES.reduce((sum, w) => sum + w.winRate, 0) / WHALES.length,
  totalVolume: WHALES.reduce((sum, w) => sum + w.volume, 0)
};

const MOCK_UPCOMING_BETS = [
  {
    id: 1,
    market: "Will the Federal Reserve cut interest rates in June?",
    side: "Yes",
    whaleOverlap: 142,
    totalVolume: 1250000,
    confidence: 88
  },
  {
    id: 2,
    market: "Who will win the 2024 US Presidential Election?",
    side: "No",
    whaleOverlap: 89,
    totalVolume: 850000,
    confidence: 72
  },
  {
    id: 3,
    market: "Will Ethereum ETFs be approved by the SEC before July?",
    side: "Yes",
    whaleOverlap: 215,
    totalVolume: 3400000,
    confidence: 94
  },
  {
    id: 4,
    market: "Will TikTok be banned in the US in 2024?",
    side: "No",
    whaleOverlap: 67,
    totalVolume: 420000,
    confidence: 65
  },
  {
    id: 5,
    market: "Will SpaceX launch Starship to orbit successfully in May?",
    side: "Yes",
    whaleOverlap: 110,
    totalVolume: 980000,
    confidence: 81
  },
  {
    id: 6,
    market: "Will Bitcoin hit $100k in 2024?",
    side: "Yes",
    whaleOverlap: 305,
    totalVolume: 5100000,
    confidence: 91
  }
];

// Exporting to global window object so it can be used across vanilla JS files
window.PolyWhaleData = {
  whales: WHALES,
  stats: MOCK_STATS,
  upcomingBets: MOCK_UPCOMING_BETS,
  formatAddress,
  formatCurrency
};
