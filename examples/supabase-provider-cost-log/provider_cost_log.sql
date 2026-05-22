-- adaptive-island Supabase source table example
--
-- This table is intentionally modeled after BabySea's documented production
-- provider_cost_log shape: one row per provider submission, resolved later to a
-- terminal outcome. Databricks reads it through Lakehouse Federation.
--
-- Security posture:
--   - RLS is enabled.
--   - No anon/authenticated policies are created by default.
--   - Insert/read from trusted backend code with the Supabase service role, or
--     add tenant-specific policies that match your application model.

begin;

create table if not exists public.provider_cost_log (
  id bigint generated always as identity primary key,
  account_id text,
  generation_id text not null,
  provider text not null,
  provider_model_id text,
  prediction_id text,
  model text not null,
  estimated_cost numeric(12, 6),
  outcome text not null default 'pending',
  attempt_order integer not null default 1,
  was_cancelled boolean not null default false,
  cancel_available boolean not null default false,
  submitted_at timestamptz not null default now(),
  resolved_at timestamptz,
  error_message text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint provider_cost_log_outcome_check
    check (outcome in ('used', 'cancelled', 'discarded', 'failed', 'pending')),
  constraint provider_cost_log_attempt_order_check
    check (attempt_order >= 1),
  constraint provider_cost_log_estimated_cost_check
    check (estimated_cost is null or estimated_cost >= 0),
  constraint provider_cost_log_resolved_after_submitted_check
    check (resolved_at is null or resolved_at >= submitted_at)
);

create index if not exists provider_cost_log_model_submitted_idx
  on public.provider_cost_log (model, submitted_at desc);

create index if not exists provider_cost_log_generation_idx
  on public.provider_cost_log (generation_id, attempt_order);

create index if not exists provider_cost_log_account_submitted_idx
  on public.provider_cost_log (account_id, submitted_at desc)
  where account_id is not null;

create or replace function public.set_provider_cost_log_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_provider_cost_log_updated_at on public.provider_cost_log;
create trigger set_provider_cost_log_updated_at
before update on public.provider_cost_log
for each row execute function public.set_provider_cost_log_updated_at();

alter table public.provider_cost_log enable row level security;

comment on table public.provider_cost_log is
  'Provider attempt log consumed by adaptive-island through Databricks Lakehouse Federation.';
comment on column public.provider_cost_log.outcome is
  'pending while in flight; terminal values are used, cancelled, discarded, or failed.';
comment on column public.provider_cost_log.attempt_order is
  '1 for initial provider, 2+ for failover attempts.';
comment on column public.provider_cost_log.metadata is
  'Small operational metadata only; do not store secrets, raw prompts, or PII unless your policies allow it.';

commit;
