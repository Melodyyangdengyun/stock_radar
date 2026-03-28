const API_BASE = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

export async function fetchStockData(symbol: string, period = "daily", days = 90) {
  const res = await fetch(`${API_BASE}/api/stocks/${symbol}?period=${period}&days=${days}`);
  return res.json();
}

export async function fetchLimitUp(date?: string) {
  const param = date ? `?date=${date}` : "";
  const res = await fetch(`${API_BASE}/api/market/limit-up${param}`);
  return res.json();
}

export async function fetchLimitDown(date?: string) {
  const param = date ? `?date=${date}` : "";
  const res = await fetch(`${API_BASE}/api/market/limit-down${param}`);
  return res.json();
}

export async function fetchSectorHeatmap() {
  const res = await fetch(`${API_BASE}/api/market/sector-heatmap`);
  return res.json();
}

export async function fetchFundFlow(symbol: string) {
  const res = await fetch(`${API_BASE}/api/stocks/${symbol}/fund-flow`);
  return res.json();
}
