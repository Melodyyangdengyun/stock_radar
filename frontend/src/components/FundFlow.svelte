<script lang="ts">
  import { onMount } from "svelte";
  import { fetchLimitUp } from "../lib/api";
  import * as echarts from "echarts";

  let chartEl: HTMLDivElement;
  let loading = $state(true);

  onMount(async () => {
    const chart = echarts.init(chartEl);

    try {
      const data = await fetchLimitUp();
      const stocks = (data.stocks ?? []).slice(0, 15);

      const option = {
        backgroundColor: "transparent",
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow" },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        yAxis: {
          type: "category",
          data: stocks.map((s: any) => s.name),
          axisLabel: { color: "#94a3b8", fontSize: 11 },
          axisLine: { lineStyle: { color: "#334155" } },
        },
        xAxis: {
          type: "value",
          axisLabel: {
            color: "#94a3b8",
            formatter: (v: number) => `${(v / 100000000).toFixed(1)}亿`,
          },
          splitLine: { lineStyle: { color: "#1e293b" } },
        },
        series: [
          {
            name: "成交额",
            type: "bar",
            data: stocks.map((s: any) => s.amount),
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: "#ef4444" },
                { offset: 1, color: "#f97316" },
              ]),
            },
          },
        ],
      };

      chart.setOption(option);
      window.addEventListener("resize", () => chart.resize());
    } catch {
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <div class="flex items-center justify-center h-64 text-slate-500">加载中...</div>
{/if}
<div bind:this={chartEl} class="w-full h-80" class:hidden={loading}></div>
