<script lang="ts">
  import { onMount } from "svelte";
  import { fetchStockData } from "../lib/api";

  interface Props {
    symbol: string;
  }

  let { symbol }: Props = $props();
  let stock = $state<any>(null);
  let loading = $state(true);

  onMount(async () => {
    try {
      const data = await fetchStockData(symbol, "daily", 30);
      const klines = data.klines ?? [];
      if (klines.length > 0) {
        const latest = klines[klines.length - 1];
        const prev = klines.length > 1 ? klines[klines.length - 2] : latest;
        stock = {
          symbol,
          price: latest.close,
          change_pct: latest.change_pct ?? ((latest.close - prev.close) / prev.close * 100),
          high: latest.high,
          low: latest.low,
          volume: latest.volume,
          amount: latest.amount,
          date: latest.date,
        };
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  function formatAmount(v: number): string {
    if (v >= 100000000) return `${(v / 100000000).toFixed(2)}亿`;
    if (v >= 10000) return `${(v / 10000).toFixed(2)}万`;
    return v.toFixed(0);
  }
</script>

{#if loading}
  <div class="card animate-pulse h-32"></div>
{:else if stock}
  <div class="card">
    <div class="flex items-baseline gap-4">
      <h1 class="text-2xl font-bold">{symbol}</h1>
      <span class="text-4xl font-bold" class:text-red-400={stock.change_pct >= 0} class:text-green-400={stock.change_pct < 0}>
        {stock.price.toFixed(2)}
      </span>
      <span class="text-lg" class:text-red-400={stock.change_pct >= 0} class:text-green-400={stock.change_pct < 0}>
        {stock.change_pct >= 0 ? "+" : ""}{stock.change_pct.toFixed(2)}%
      </span>
    </div>
    <div class="grid grid-cols-4 gap-4 mt-4 text-sm">
      <div>
        <span class="text-slate-400">最高</span>
        <p class="text-red-400">{stock.high.toFixed(2)}</p>
      </div>
      <div>
        <span class="text-slate-400">最低</span>
        <p class="text-green-400">{stock.low.toFixed(2)}</p>
      </div>
      <div>
        <span class="text-slate-400">成交量</span>
        <p>{formatAmount(stock.volume)}</p>
      </div>
      <div>
        <span class="text-slate-400">成交额</span>
        <p>{formatAmount(stock.amount)}</p>
      </div>
    </div>
  </div>
{:else}
  <div class="card text-slate-500">无法加载股票数据</div>
{/if}
