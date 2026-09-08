import { readFileSync } from 'fs';

export function services() {
  return JSON.parse(readFileSync('src/data/services.json', 'utf-8')).services;
}

export function testimonials() {
  return JSON.parse(readFileSync('src/data/testimonials.json', 'utf-8')).testimonials;
}

export function galleries() {
  return JSON.parse(readFileSync('src/data/galleries.json', 'utf-8')).galleries;
}

export function latestGalleries(n) {
  return galleries().slice(0, n);
}