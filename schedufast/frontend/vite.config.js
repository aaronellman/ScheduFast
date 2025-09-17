import { defineConfig } from 'vite';

export default defineConfig({
  root: 'src',
  build: {
    rollupOptions: {
      input: {
        main: 'src/index.html',
        signup: 'src/signup.html',
      },
    },
  },
});