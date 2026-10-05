import { defineConfig } from 'astro/config';
import { generateSitemap } from './tools/generate-sitemap.mjs';

export default defineConfig({
  site: 'https://michalgazda.github.io',
  base: '/annamatejska.pl/',
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
