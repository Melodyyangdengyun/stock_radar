<script lang="ts">
  import { onMount } from "svelte";
  import { fetchLimitUp, fetchLimitDown, fetchSectorHeatmap } from "../lib/api";

  interface Props {
    title: string;
    type: "limit-up" | "limit-down" | "sector-up" | "sector-down";
  }

  let { title, type }: Props = $props();
  let value = $state("--");
  let loading = $state(true);

  onMount(async () => {
    try {
      if (type === "limit-up") {
        const data = await fetchLimitUp();
        value = String(data.count ?? 0);
      } else if (type === "limit-down") {
        const data = await fetchLimitDown();
        value = String(data.count ?? 0);
      } else {
        const data = await fetchSectorHeatmap();
        const sectors = data.sectors ?? [];
        if (type === "sector-up") {
          value = String(sectors.filter((s: any) => s.change_pct > 0).length);
        } else {
          value = String(sectors.filter((s: any) => s.change_pct < 0).length);
        }
      }
    } catch {
      value = "N/A";
    } finally {
      loading = false;
    }
  });
</script>

<div class="card">
  <p class="text-sm text-slate-400">{title}</p>
  <p class="text-3xl font-bold mt-2" class:text-red-400={type === "limit-up"} class:text-green-400={type === "limit-down"}>
    {loading ? "..." : value}
  </p>
</div>
