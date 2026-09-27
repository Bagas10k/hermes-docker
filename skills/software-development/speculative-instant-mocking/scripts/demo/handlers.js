import { http, HttpResponse } from 'msw';
// Handlers provide deterministic synthetic responses labelled explicitly.
export const handlers = [
  http.get('/api/seed', () => HttpResponse.json({ synthetic: true, seed: 7, count: 6, maxBuffer: 20 })),
  http.get('/api/health', () => HttpResponse.json({ synthetic: true, status: 'ok', mockEngine: 'MSW 2.x' }))
];
