import { defineConfig } from "astro/config";
import svelte from "@astrojs/svelte";
import tailwindcss from "@tailwindcss/vite";
import node from "@astrojs/node";

export default defineConfig({
  integrations: [svelte()],
  vite: {
    plugins: [tailwindcss()],
  },
  output: "static",
  adapter: node({
    mode: "standalone",
  }),
  server: {
    host: "0.0.0.0",
    port: 4321,
  },
});
