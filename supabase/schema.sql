-- Heimabend-Baukasten: Tabellen und Zugriffsregeln für Supabase
-- Stand: 07.09.2026 · Entwurf, siehe docs/gemeinsam-sammeln.md
-- Im Supabase-Dashboard unter "SQL Editor" einfügen und ausführen.
-- Mehrfach ausführbar (create ... if not exists / drop policy if exists).

-- ---------------------------------------------------------------- Profile
-- Ein Profil je Konto. Nur Anzeigename und Rolle, keine E-Mail.
create table if not exists public.profile (
  id          uuid primary key references auth.users (id) on delete cascade,
  anzeigename text not null default '' check (char_length(anzeigename) <= 60),
  rolle       text not null default 'mitglied' check (rolle in ('mitglied', 'redaktion')),
  erstellt    timestamptz not null default now()
);

-- Profil automatisch anlegen, wenn sich jemand zum ersten Mal anmeldet.
create or replace function public.profil_anlegen()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profile (id, anzeigename)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'name', ''))
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists profil_bei_neuem_konto on auth.users;
create trigger profil_bei_neuem_konto
  after insert on auth.users
  for each row execute function public.profil_anlegen();

-- Hilfsfunktion: ist die angemeldete Person Redaktion?
create or replace function public.ist_redaktion()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profile where id = auth.uid() and rolle = 'redaktion');
$$;

-- -------------------------------------------------------------- Beiträge
create table if not exists public.beitraege (
  id          uuid primary key default gen_random_uuid(),
  autor_id    uuid not null references auth.users (id) on delete cascade,
  autor_name  text not null default '',
  status      text not null default 'entwurf'
              check (status in ('entwurf', 'eingereicht', 'freigegeben', 'abgelehnt')),
  lizenz      text not null default 'CC BY-SA 4.0',
  -- Der Baustein selbst, Felder wie in data/SCHEMA.md (titel, bereich, umfang, ...)
  element     jsonb not null,
  bemerkung   text not null default '',   -- Rückmeldung der Redaktion
  erstellt    timestamptz not null default now(),
  geaendert   timestamptz not null default now(),
  constraint element_hat_titel   check (element ? 'titel' and char_length(element ->> 'titel') between 1 and 120),
  constraint element_hat_bereich check ((element ->> 'bereich') in
    ('spiel', 'pfadfindertechnik', 'natur_draussen', 'werken', 'kochen', 'musisch', 'gemeinschaft')),
  constraint element_hat_umfang  check ((element ->> 'umfang') in ('baustein', 'ganzer_abend'))
);

create index if not exists beitraege_status on public.beitraege (status);
create index if not exists beitraege_autor  on public.beitraege (autor_id);

-- geaendert bei jeder Änderung setzen
create or replace function public.setze_geaendert()
returns trigger language plpgsql as $$
begin
  new.geaendert := now();
  return new;
end $$;

drop trigger if exists beitraege_geaendert on public.beitraege;
create trigger beitraege_geaendert
  before update on public.beitraege
  for each row execute function public.setze_geaendert();

-- ------------------------------------------------------ Zugriffsregeln (RLS)
alter table public.profile   enable row level security;
alter table public.beitraege enable row level security;

-- Profile: jeder liest Anzeigenamen, jeder bearbeitet nur sein eigenes Profil,
-- die Rolle kann nur die Redaktion ändern.
drop policy if exists "profile lesen"       on public.profile;
drop policy if exists "eigenes profil"      on public.profile;
create policy "profile lesen"  on public.profile for select using (true);
create policy "eigenes profil" on public.profile for update
  using (id = auth.uid())
  with check (id = auth.uid() and (rolle = (select rolle from public.profile where id = auth.uid()) or public.ist_redaktion()));

-- Beiträge lesen: freigegebene für alle (auch ohne Konto), eigene immer, Redaktion alles.
drop policy if exists "beitraege lesen" on public.beitraege;
create policy "beitraege lesen" on public.beitraege for select
  using (status = 'freigegeben' or autor_id = auth.uid() or public.ist_redaktion());

-- Einreichen: nur angemeldet, nur unter eigenem Namen, nur als Entwurf oder eingereicht.
drop policy if exists "beitrag anlegen" on public.beitraege;
create policy "beitrag anlegen" on public.beitraege for insert
  with check (auth.uid() = autor_id and status in ('entwurf', 'eingereicht'));

-- Bearbeiten: eigene Beiträge, solange sie nicht freigegeben sind; Redaktion alles.
drop policy if exists "beitrag bearbeiten" on public.beitraege;
create policy "beitrag bearbeiten" on public.beitraege for update
  using (public.ist_redaktion() or (autor_id = auth.uid() and status <> 'freigegeben'))
  with check (public.ist_redaktion() or (autor_id = auth.uid() and status in ('entwurf', 'eingereicht')));

-- Löschen: eigene Entwürfe; Redaktion alles.
drop policy if exists "beitrag loeschen" on public.beitraege;
create policy "beitrag loeschen" on public.beitraege for delete
  using (public.ist_redaktion() or (autor_id = auth.uid() and status = 'entwurf'));

-- ------------------------------------------------------------ Erste Redaktion
-- Nach der ersten Anmeldung im Dashboard einmal ausführen (E-Mail anpassen):
-- update public.profile set rolle = 'redaktion'
--   where id = (select id from auth.users where email = 'deine@adresse.de');
