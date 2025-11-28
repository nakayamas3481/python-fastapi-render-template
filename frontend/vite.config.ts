import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  server: {
    proxy: {
      '/api' : {
        target: 'http://localhost:8000',
        changeOrigin : true,
        secure: false,
      },
      '/uploads' : {
        target: 'http://localhost:8000',
        changeOrigin : true,
        secure: false,
      }
    }
  }, 
  // ★追加: shadcnが使う alias を Vite に教える
  resolve: {
    alias: {
      "~": path.resolve(__dirname, "app"),
      "@": path.resolve(__dirname, "app"),
    },
  },
  plugins: [tailwindcss(), reactRouter(), tsconfigPaths()],
});
