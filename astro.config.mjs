import { defineConfig } from 'astro/config';
import { generateSitemap } from './tools/generate-sitemap.mjs';

export default defineConfig({
  // Served from the root of the custom domain (annamatejska.pl → GitHub Pages),
  // so there is no base path any more. BASE_URL is '/' everywhere.
  site: 'https://annamatejska.pl',
  base: '/',
  output: 'static',
  outDir: './dist',
  integrations: [
    {
      name: 'sitemap-from-canonicals',
      hooks: {
        'astro:build:done': async ({ dir }) => {
          const n = generateSitemap({ dist: dir.pathname.replace(/\/$/, '') });
          console.log(`sitemap.xml generated: ${n} URLs`);
        },
      },
    },
  ],
});
