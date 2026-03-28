<script lang="ts">
  import { onMount } from "svelte";
  import { createChart, type IChartApi } from "lightweight-charts";
  import { fetchStockData } from "../lib/api";

  interface Props {
    symbol: string;
    period?: string;
    days?: number;
  }

  let { symbol, period = "daily", days = 90 }: Props = $props();
  let chartEl: HTMLDivElement;
  let loading = $state(true);
  let chart: IChartApi;

  onMount(async () => {
    chart = createChart(chartEl, {
      width: chartEl.clientWidth,
      height: 400,
      layout: {
        background: { color: "transparent" },
        textColor: "#94a3b8",
      },
      grid: {
        vertLines: { color: "#1e293b" },
        horzLines: { color: "#1e293b" },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: "#334155",
      },
      timeScale: {
        borderColor: "#334155",
        timeVisible: false,
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#ef4444",
      downColor: "#22c55e",
      borderDownColor: "#22c55e",
      borderUpColor: "#ef4444",
      wickDownColor: "#22c55e",
      wickUpColor: "#ef4444",
    });

    const volumeSeries = chart.addHistogramSeries({
      color: "#3b82f6",
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    try {
      const data = await fetchStockData(symbol, period, days);
      const klines = data.klines ?? [];

      candlestickSeries.setData(
        klines.map((k: any) => ({
          time: k.date,
          open: k.open,
          high: k.high,
          low: k.low,
          close: k.close,
        }))
      );

      volumeSeries.setData(
        klines.map((k: any) => ({
          time: k.date,
          value: k.volume,
          color: k.close >= k.open ? "#ef444466" : "#22c55e66",
        }))
      );

      chart.timeScale().fitContent();
    } catch (e) {
      console.error("Failed to load K-line data:", e);
    } finally {
      loading = false;
    }

    const resizeObserver = new ResizeObserver(() => {
      chart.applyOptions({ width: chartEl.clientWidth });
    });
    resizeObserver.observe(chartEl);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  });
</script>

{#if loading}
  <div class="flex items-center justify-center h-96 text-slate-500">加载K线数据...</div>
{/if}
<div bind:this={chartEl} class="w-full" class:hidden={loading}></div>
