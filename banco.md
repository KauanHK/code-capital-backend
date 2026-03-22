CREATE TABLE category (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(100) NOT NULL
);

CREATE TABLE service (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(100) NOT NULL,
  category_id UUID NOT NULL REFERENCES category(id)
);

CREATE TABLE client (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(150) NOT NULL,
  cpf_cnpj    VARCHAR(18) UNIQUE,
  email       VARCHAR(150),
  phone       VARCHAR(20),
  type        VARCHAR(2) CHECK (type IN ('pj', 'pf')),
  created_at  TIMESTAMP DEFAULT now()
);

CREATE TABLE transaction (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       UUID REFERENCES client(id),          -- nullable
  service_id      UUID NOT NULL REFERENCES service(id),
  is_expense      BOOLEAN NOT NULL,
  is_personal     BOOLEAN NOT NULL DEFAULT false,
  pjpf            VARCHAR(2) CHECK (pjpf IN ('pj', 'pf')),
  amount          NUMERIC(12, 2) NOT NULL,
  description     TEXT,
  status          VARCHAR(20) DEFAULT 'pending'
                    CHECK (status IN ('pending', 'paid', 'cancelled')),
  payment_method  VARCHAR(20)
                    CHECK (payment_method IN ('pix', 'cash', 'card', 'transfer')),
  transaction_date DATE NOT NULL,
  created_at      TIMESTAMP DEFAULT now()
);