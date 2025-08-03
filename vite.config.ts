import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";

// import sparkPlugin from "@github/spark/spark-vite-plugin";
// import createIconImportProxy from "@github/spark/vitePhosphorIconProxyPlugin";
import { resolve } from 'path'

const projectRoot = process.env.PROJECT_ROOT || process.cwd()

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // DO NOT REMOVE - temporarily commented out due to package issues
    // createIconImportProxy() as PluginOption,
    // sparkPlugin() as PluginOption,
  ],
  resolve: {
    alias: {
      '@': resolve(projectRoot, 'src')
    }
  },
});
