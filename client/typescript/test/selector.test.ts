import { describe, it, expect } from 'vitest';

import { Selector, resolveAdaptiveRoutingEnabled, type CacheClient } from '../src/index';

class StubCache implements CacheClient {
  readonly keys: string[] = [];

  constructor(private readonly payload: string | null) {}
  async get(key: string): Promise<string | null> {
    this.keys.push(key);
    return this.payload;
  }
}

function rankingPayload(overrides: Record<string, unknown> = {}): string {
  return JSON.stringify({
    providers_ranked: ['b', 'a'],
    scores: { b: 0.9, a: 0.1 },
    attempts_total: 180,
    window_hours: 24,
    computed_at: '2026-04-29T00:00:00Z',
    ...overrides,
  });
}

describe('Selector', () => {
  it('falls back deterministically when cache is empty', async () => {
    const sel = new Selector({ cache: new StubCache(null) });
    const provider = await sel.pick({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b', 'c'],
    });
    expect(provider).toBe('a');
    expect(sel.lastDecision?.source).toBe('fallback');
    expect(sel.lastDecision?.providers).toEqual(['a', 'b', 'c']);
  });

  it('returns cached ranking order on a cache hit', async () => {
    const cache = new StubCache(rankingPayload());
    const sel = new Selector({ cache });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['b', 'a']);
    expect(cache.keys).toEqual(['predictive:ranking:us:demo/model']);
    expect(sel.lastDecision?.source).toBe('cached-ranking');
  });

  it('skips cache and returns fallback when adaptive routing is disabled', async () => {
    const cache = new StubCache(rankingPayload());
    const sel = new Selector({ cache, adaptiveRoutingEnabled: false });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(cache.keys).toEqual([]);
    expect(sel.lastDecision?.source).toBe('adaptive-disabled');
  });

  it('parses adaptive routing disabled aliases like production', () => {
    expect(resolveAdaptiveRoutingEnabled(undefined)).toBe(true);
    expect(resolveAdaptiveRoutingEnabled(null)).toBe(true);
    expect(resolveAdaptiveRoutingEnabled('')).toBe(true);
    expect(resolveAdaptiveRoutingEnabled('true')).toBe(true);
    expect(resolveAdaptiveRoutingEnabled('FALSE')).toBe(false);
    expect(resolveAdaptiveRoutingEnabled(' 0 ')).toBe(false);
    expect(resolveAdaptiveRoutingEnabled('off')).toBe(false);
    expect(resolveAdaptiveRoutingEnabled('disabled')).toBe(false);
  });

  it('accepts valid RFC3339 offset computed_at values', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ computed_at: '2026-04-29T00:30:00+02:00' })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['b', 'a']);
    expect(sel.lastDecision?.source).toBe('cached-ranking');
  });

  it('reports fallback when cached providers do not overlap fallback providers', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ providers_ranked: ['x'], scores: { x: 1.0 } })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('serves only the ranked subset of fallback when ranking omits some providers', async () => {
    // Match BabySea production: fallback providers absent from the ranking
    // are not appended onto the served order. The ranking is the source of
    // truth when a non-empty intersection exists.
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ providers_ranked: ['b'], scores: { b: 0.9 } })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b', 'c'],
    });
    expect(order).toEqual(['b']);
    expect(sel.lastDecision?.source).toBe('cached-ranking');
  });

  it('falls back on malformed cache payloads', async () => {
    const sel = new Selector({
      cache: new StubCache(JSON.stringify({ providers_ranked: ['b', 'a'] })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('falls back on invalid computed_at values', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ computed_at: 'not-a-date' })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('falls back on timezone-less computed_at values', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ computed_at: '2026-04-29T00:00:00' })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('falls back when a ranked provider has no score', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ scores: { b: 0.9 } })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('falls back on boolean scores', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ scores: { b: true, a: 0.1 } })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('falls back on non-finite scores', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ scores: { b: 1e999, a: 0.1 } })),
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('falls back on stale rankings when maxCacheAgeSeconds is set', async () => {
    const sel = new Selector({
      cache: new StubCache(rankingPayload({ computed_at: '2020-01-01T00:00:00Z' })),
      maxCacheAgeSeconds: 1,
    });
    const order = await sel.rank({
      modelId: 'demo/model',
      region: 'us',
      fallback: ['a', 'b'],
    });
    expect(order).toEqual(['a', 'b']);
    expect(sel.lastDecision?.source).toBe('fallback');
  });

  it('builds an attempt.v1 event', () => {
    const sel = new Selector();
    const ev = sel.buildAttempt({
      modelId: 'demo/model',
      provider: 'a',
      outcome: 'used',
      estimatedCost: 0.001,
    });
    expect(ev.schema_version).toBe('attempt.v1');
    expect(ev.provider).toBe('a');
    expect(ev.model).toBe('demo/model');
    expect(ev.outcome).toBe('used');
    expect(typeof ev.generation_id).toBe('string');
  });
});
