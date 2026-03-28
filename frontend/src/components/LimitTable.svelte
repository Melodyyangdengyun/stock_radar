<script lang="ts">
  import { onMount } from "svelte";
  import { fetchLimitUp, fetchLimitDown } from "../lib/api";

  interface Props {
    type: "limit-up" | "limit-down";
  }

  let { type }: Props = $props();
  let stocks = $state<any[]>([]);
  let loading = $state(true);

  function formatAmount(v: number): string {
    if (v >= 100000000) return `${(v / 100000000).toFixed(2)}亿`;
    if (v >= 10000) return `${(v / 10000).toFixed(2)}万`;
    return v.toFixed(0);
  }

  onMount(async () => {
    try {
      const data = type === "limit-up" ? await fetchLimitUp() : await fetchLimitDown();
      stocks = data.stocks ?? [];
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <div class="text-slate-500 text-center py-8">加载中...</div>
{:else if stocks.length === 0}
  <div class="text-slate-500 text-center py-8">暂无数据</div>
{:else}
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead>
        <tr class="text-slate-400 border-b border-slate-700">
          <th class="text-left py-2 px-2">代码</th>
          <th class="text-left py-2 px-2">名称</th>
          <th class="text-right py-2 px-2">涨跌幅</th>
          <th class="text-right py-2 px-2">成交额</th>
          <th class="text-right py-2 px-2">换手率</th>
          {#if type === "limit-up"}
            <th class="text-right py-2 px-2">连板</th>
          {/if}
        </tr>
      </thead>
      <tbody>
        {#each stocks.slice(0, 20) as stock}
          <tr class="border-b border-slate-800 hover:bg-slate-800/50 cursor-pointer" onclick={() => window.location.href = `/stocks/${stock.code}`}>
            <td class="py-2 px-2 text-blue-400">{stock.code}</td>
            <td class="py-2 px-2">{stock.name}</td>
            <td class="py-2 px-2 text-right" class:text-red-400={stock.change_pct >= 0} class:text-green-400={stock.change_pct < 0}>
              {stock.change_pct >= 0 ? "+" : ""}{stock.change_pct.toFixed(2)}%
            </td>
            <td class="py-2 px-2 text-right">{formatAmount(stock.amount)}</td>
            <td class="py-2 px-2 text-right">{stock.turnover.toFixed(2)}%</td>
            {#if type === "limit-up"}
              <td class="py-2 px-2 text-right text-yellow-400">{stock.consecutive_days ?? 1}板</td>
            {/if}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}
