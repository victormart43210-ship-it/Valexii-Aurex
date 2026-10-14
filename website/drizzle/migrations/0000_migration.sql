CREATE TABLE public.inquiries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  kind text NOT NULL CHECK (kind IN ('contact','partnership')),
  name text NOT NULL CHECK (char_length(name) BETWEEN 1 AND 100),
  email text NOT NULL CHECK (char_length(email) BETWEEN 3 AND 254),
  organization text CHECK (organization IS NULL OR char_length(organization) <= 150),
  category text NOT NULL CHECK (char_length(category) <= 80),
  message text NOT NULL CHECK (char_length(message) BETWEEN 10 AND 4000),
  dedupe_hash text NOT NULL,
  notified_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX inquiries_email_created_idx ON public.inquiries (email, created_at DESC);
CREATE UNIQUE INDEX inquiries_dedupe_idx ON public.inquiries (dedupe_hash);
GRANT ALL ON public.inquiries TO service_role;
ALTER TABLE public.inquiries ENABLE ROW LEVEL SECURITY;

CREATE TABLE public.early_access_leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE CHECK (char_length(email) BETWEEN 3 AND 254),
  device text CHECK (device IS NULL OR char_length(device) <= 80),
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','confirmed')),
  confirm_token_hash text NOT NULL,
  consent_at timestamptz NOT NULL,
  confirmed_at timestamptz,
  last_requested_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX early_access_token_idx ON public.early_access_leads (confirm_token_hash);
GRANT ALL ON public.early_access_leads TO service_role;
ALTER TABLE public.early_access_leads ENABLE ROW LEVEL SECURITY;
-- No anon/authenticated grants or policies: only server code (service role) can read/write.