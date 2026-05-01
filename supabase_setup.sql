-- =============================================================
-- GeoChange — Supabase Database Setup
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New query)
-- =============================================================

-- 1. Profiles table (extends Supabase Auth users)
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  username    text unique not null,
  email       text unique not null,
  created_at  timestamptz default now(),
  last_login  timestamptz default now(),

  -- Subscription
  subscription_plan    text default 'trial',       -- trial, monthly, yearly
  subscription_active  boolean default false,
  subscription_expires timestamptz,
  trial_expires        timestamptz
);

-- 2. Enable Row Level Security
alter table public.profiles enable row level security;

-- 3. RLS Policies: users can read/update only their own profile
create policy "Users can view own profile"
  on public.profiles for select
  using (auth.uid() = id);

create policy "Users can update own profile"
  on public.profiles for update
  using (auth.uid() = id);

-- 4. Allow insert for new registrations (service role or trigger)
create policy "Allow insert for authenticated users"
  on public.profiles for insert
  with check (auth.uid() = id);

-- 5. Auto-create profile on signup via trigger
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, username, email, trial_expires)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'username', split_part(new.email, '@', 1)),
    new.email,
    now() + interval '1 day'
  );
  return new;
end;
$$ language plpgsql security definer;

-- Drop trigger if exists, then create
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- 6. Admin view: all users (for service_role key only, not anon)
-- You can view all users in Supabase Dashboard → Table Editor → profiles
