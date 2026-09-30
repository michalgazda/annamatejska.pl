import { readFileSync } from 'fs';

export function site() {
  return JSON.parse(readFileSync('src/data/site.json', 'utf-8'));
}

export function services() {
  return JSON.parse(readFileSync('src/data/services.json', 'utf-8')).services;
}

export function testimonials() {
  return JSON.parse(readFileSync('src/data/testimonials.json', 'utf-8')).testimonials;
}

export function galleries() {
  return JSON.parse(readFileSync('src/data/galleries.json', 'utf-8')).galleries;
}

// Shared Polish long-date formatter (used by galerie listing + detail)
const months = ['stycznia','lutego','marca','kwietnia','maja','czerwca','lipca','sierpnia','września','października','listopada','grudnia'];
export function formatDate(d) {
  const p = d.split('-');
  return `${parseInt(p[2])} ${months[parseInt(p[1])-1]} ${p[0]}`;
}