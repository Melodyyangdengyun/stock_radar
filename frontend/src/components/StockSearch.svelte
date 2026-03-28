<script lang="ts">
  let searchQuery = $state("");

  function handleSearch() {
    if (searchQuery.trim()) {
      window.location.href = `/stocks/${searchQuery.trim()}`;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Enter") handleSearch();
  }
</script>

<div class="flex gap-2">
  <input
    type="text"
    bind:value={searchQuery}
    onkeydown={handleKeydown}
    placeholder="输入股票代码 (如 000001)"
    class="bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
  />
  <button
    onclick={handleSearch}
    class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition"
  >
    查询
  </button>
</div>
