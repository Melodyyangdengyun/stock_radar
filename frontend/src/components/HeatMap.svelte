<script lang="ts">
  import { onMount } from "svelte";
  import { fetchSectorHeatmap } from "../lib/api";
  import * as echarts from "echarts";

  let chartEl: HTMLDivElement;
  let loading = $state(true);

  onMount(async () => {
    const chart = echarts.init(chartEl);

    try {
      const data = await fetchSectorHeatmap();
      const sectors = (data.sectors ?? []).slice(0, 30);

      const option = {
        backgroundColor: "transparent",
        tooltip: {
          formatter: (params: any) =>
            `${params.data.name}<br/>涨跌幅: ${params.data.value[2].toFixed(2)}%`,
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: sectors.map((s: any) => s.name),
          axisLabel: {
            rotate: 45,
            color: "#94a3b8",
            fontSize: 10,
          },
          axisLine: { lineStyle: { color: "#334155" } },
        },
        yAxis: {
          type: "value",
          axisLabel: { color: "#94a3b8" },
          splitLine: { lineStyle: { color: "#1e293b" } },
        },
        series: [
          {
            type: "bar",
            data: sectors.map((s: any) => ({
              value: s.change_pct,
              itemStyle: {
                color: s.change_pct >= 0 ? "#ef4444" : "#22c55e",
              },
            })),
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
