/**
 * adaptive-island TypeScript SDK.
 *
 * Reads adaptive-island provider rankings shaped after BabySea's documented
 * cache contract, returns an ordered provider list, and fails open to
 * caller-provided fallback order.
 */

export interface Ranking {
  providers_ranked: string[];
  scores: Record<string, number>;
  attempts_total: number;
  window_hours: number;
  computed_at: string;
}

export interface Attempt {
  schema_version: 'attempt.v1';
  generation_id: string;
  account_id: string | null;
  provider: string;
  provider_model_id: string | null;
  prediction_id: string | null;
  model: string;
  estimated_cost: number | null;
  outcome: 'used' | 'cancelled' | 'discarded' | 'failed' | 'pending';
  attempt_order: number;
  was_cancelled: boolean;
  cancel_available: boolean;
  submitted_at: string;
  resolved_at: string | null;
  error_message: string | null;
  metadata: Record<string, unknown>;
}

export interface CacheClient {
  get(key: string): Promise<string | null>;
}

export interface SelectorOptions {
  cache?: CacheClient;
  keyPrefix?: string;
  maxCacheAgeSeconds?: number;
  adaptiveRoutingEnabled?: boolean;
}

export interface Decision {
  provider: string;
  providers: string[];
  source: 'cached-ranking' | 'fallback' | 'adaptive-disabled';
}

const ADAPTIVE_ROUTING_DISABLED_VALUES = new Set(['false', '0', 'off', 'disabled']);

export function resolveAdaptiveRoutingEnabled(value: string | null | undefined): boolean {
  if (value === null || value === undefined || value.trim().length === 0) return true;
  return !ADAPTIVE_ROUTING_DISABLED_VALUES.has(value.trim().toLowerCase());
}

export class Selector {
  private readonly cache: CacheClient | undefined;
  private readonly keyPrefix: string;
  private readonly maxCacheAgeMs: number | undefined;
  private readonly adaptiveRoutingEnabled: boolean;
  private lastDecisionInternal: Decision | null = null;

  constructor(opts: SelectorOptions = {}) {
    if (opts.maxCacheAgeSeconds !== undefined && opts.maxCacheAgeSeconds <= 0) {
      throw new Error('adaptive-island: maxCacheAgeSeconds must be positive.');
    }
    this.cache = opts.cache;
    this.keyPrefix = opts.keyPrefix ?? 'predictive:ranking';
    this.maxCacheAgeMs = opts.maxCacheAgeSeconds === undefined ? undefined : opts.maxCacheAgeSeconds * 1000;
    this.adaptiveRoutingEnabled = opts.adaptiveRoutingEnabled ?? true;
  }

  get lastDecision(): Decision | null {
    return this.lastDecisionInternal;
  }

  async rank(input: {
    modelId: string;
    region: string;
    fallback: string[];
  }): Promise<string[]> {
    if (input.fallback.length === 0) {
      throw new Error('adaptive-island: fallback must contain at least one provider.');
    }

    const fallback = [...new Set(input.fallback)];

    if (!this.adaptiveRoutingEnabled) {
      this.lastDecisionInternal = {
        provider: fallback[0]!,
        providers: fallback,
        source: 'adaptive-disabled',
      };
      return fallback;
    }

    const ranking = await this.readRanking(input);
    const allowed = new Set(fallback);

    if (ranking && ranking.length > 0) {
      // Match BabySea production semantics: trust the ranking and serve only
      // its intersection with the configured providers. Configured providers
      // not present in the ranking are intentionally excluded so adaptive
      // routing reflects observed performance, not configuration order.
      const ordered = ranking.filter((provider) => allowed.has(provider));
      if (ordered.length === 0) {
        this.lastDecisionInternal = {
          provider: fallback[0]!,
          providers: fallback,
          source: 'fallback',
        };
        return fallback;
      }
      this.lastDecisionInternal = {
        provider: ordered[0]!,
        providers: ordered,
        source: 'cached-ranking',
      };
      return ordered;
    }

    this.lastDecisionInternal = {
      provider: fallback[0]!,
      providers: fallback,
      source: 'fallback',
    };
    return fallback;
  }

  async pick(input: {
    modelId: string;
    region: string;
    fallback: string[];
  }): Promise<string> {
    return (await this.rank(input))[0]!;
  }

  buildAttempt(input: {
    modelId: string;
    provider: string;
    outcome: Attempt['outcome'];
    generationId?: string;
    accountId?: string | null;
    providerModelId?: string | null;
    predictionId?: string | null;
    estimatedCost?: number | null;
    attemptOrder?: number;
    wasCancelled?: boolean;
    cancelAvailable?: boolean;
    submittedAt?: string;
    resolvedAt?: string | null;
    errorMessage?: string | null;
    metadata?: Record<string, unknown>;
  }): Attempt {
    return {
      schema_version: 'attempt.v1',
      generation_id: input.generationId ?? cryptoRandomId(),
      account_id: input.accountId ?? null,
      provider: input.provider,
      provider_model_id: input.providerModelId ?? null,
      prediction_id: input.predictionId ?? null,
      model: input.modelId,
      estimated_cost: input.estimatedCost ?? null,
      outcome: input.outcome,
      attempt_order: input.attemptOrder ?? 1,
      was_cancelled: input.wasCancelled ?? false,
      cancel_available: input.cancelAvailable ?? false,
      submitted_at: input.submittedAt ?? new Date().toISOString(),
      resolved_at: input.resolvedAt ?? null,
      error_message: input.errorMessage ?? null,
      metadata: input.metadata ?? {},
    };
  }

  private async readRanking(input: {
    modelId: string;
    region: string;
  }): Promise<string[] | null> {
    if (!this.cache) return null;
    const key = `${this.keyPrefix}:${input.region}:${input.modelId}`;
    try {
      const raw = await this.cache.get(key);
      if (!raw) return null;
      const parsed: unknown = JSON.parse(raw);
      if (!isRanking(parsed, this.maxCacheAgeMs)) return null;
      return parsed.providers_ranked.filter(
        (provider): provider is string => typeof provider === 'string' && provider.length > 0,
      );
    } catch {
      return null;
    }
  }
}

function isRanking(value: unknown, maxCacheAgeMs?: number): value is Ranking {
  if (!value || typeof value !== 'object') return false;
  const ranking = value as Partial<Ranking>;
  if (!Array.isArray(ranking.providers_ranked) || ranking.providers_ranked.length === 0) {
    return false;
  }
  if (!ranking.providers_ranked.every((provider) => typeof provider === 'string' && provider.length > 0)) {
    return false;
  }
  if (!ranking.scores || typeof ranking.scores !== 'object') return false;
  if (!ranking.providers_ranked.every((provider) => Object.prototype.hasOwnProperty.call(ranking.scores, provider))) {
    return false;
  }
  if (!Object.entries(ranking.scores).every(([provider, score]) => typeof provider === 'string' && typeof score === 'number' && Number.isFinite(score))) {
    return false;
  }
  const attemptsTotal = ranking.attempts_total;
  const windowHours = ranking.window_hours;
  if (!Number.isInteger(attemptsTotal) || typeof attemptsTotal !== 'number' || attemptsTotal < 0) return false;
  if (!Number.isInteger(windowHours) || typeof windowHours !== 'number' || windowHours <= 0) return false;
  if (!isRfc3339DateTime(ranking.computed_at)) return false;
  const computedAtMs = Date.parse(ranking.computed_at);
  if (!Number.isFinite(computedAtMs)) return false;
  if (maxCacheAgeMs !== undefined && Date.now() - computedAtMs > maxCacheAgeMs) return false;
  return true;
}

function isRfc3339DateTime(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const match = value.match(
    /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|([+-])(\d{2}):(\d{2}))$/,
  );
  if (!match) return false;

  const year = Number(match[1]!);
  const month = Number(match[2]!);
  const day = Number(match[3]!);
  const hour = Number(match[4]!);
  const minute = Number(match[5]!);
  const second = Number(match[6]!);
  const offsetHour = match[8] === undefined ? 0 : Number(match[8]);
  const offsetMinute = match[9] === undefined ? 0 : Number(match[9]);
  if (month < 1 || month > 12) return false;
  if (day < 1 || day > daysInMonth(year, month)) return false;
  if (hour > 23 || minute > 59 || second > 59) return false;
  if (offsetHour > 23 || offsetMinute > 59) return false;
  const parsed = new Date(value);
  return Number.isFinite(parsed.getTime());
}

function daysInMonth(year: number, month: number): number {
  return new Date(Date.UTC(year, month, 0)).getUTCDate();
}

function cryptoRandomId(): string {
  // Works in Node 18+ and modern browsers.
  const g = globalThis as unknown as { crypto?: { randomUUID?: () => string } };
  if (g.crypto?.randomUUID) return g.crypto.randomUUID().replace(/-/g, '');
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}
