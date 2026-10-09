import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],worker:{format:'es'},build:{rollupOptions:{output:{manualChunks:{charts:['recharts'],three:['three']}}}},server:{proxy:{'/api':'http://127.0.0.1:8000','/ws':{target:'ws://127.0.0.1:8000',ws:true}}},test:{environment:'jsdom',include:['src/**/*.test.tsx','src/**/*.test.ts']}});
