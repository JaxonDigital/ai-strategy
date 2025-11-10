-- Multi-Tenant MVP Database Schema
-- Created: November 4, 2025
-- Purpose: Credit-gated multi-tenant SaaS platform for Jaxon AI agents

-- ============================================================================
-- TABLE: workspaces
-- Purpose: Customer accounts (agencies or end clients)
-- ============================================================================

CREATE TABLE IF NOT EXISTS workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  api_key TEXT UNIQUE NOT NULL,
  stripe_customer_id TEXT,
  credits_remaining INTEGER DEFAULT 0 CHECK (credits_remaining >= 0),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workspaces_api_key ON workspaces(api_key);
CREATE INDEX IF NOT EXISTS idx_workspaces_email ON workspaces(email);

COMMENT ON TABLE workspaces IS 'Customer accounts with credit balances';
COMMENT ON COLUMN workspaces.api_key IS 'Authentication token format: jax_{32_random_chars}';
COMMENT ON COLUMN workspaces.credits_remaining IS 'Current credit balance, cannot go negative';

-- ============================================================================
-- TABLE: optimizely_credentials
-- Purpose: Credential vault for Optimizely DXP credentials per workspace
-- ============================================================================

CREATE TABLE IF NOT EXISTS optimizely_credentials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  project_name TEXT NOT NULL,
  dxp_api_key TEXT NOT NULL,
  dxp_api_secret TEXT NOT NULL,
  slack_webhook_url TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(workspace_id, project_name)
);

CREATE INDEX IF NOT EXISTS idx_credentials_workspace ON optimizely_credentials(workspace_id);
CREATE INDEX IF NOT EXISTS idx_credentials_project ON optimizely_credentials(workspace_id, project_name);

COMMENT ON TABLE optimizely_credentials IS 'Credential vault for Optimizely DXP projects';
COMMENT ON COLUMN optimizely_credentials.dxp_api_key IS 'TODO: Encrypt in production using pgcrypto';
COMMENT ON COLUMN optimizely_credentials.dxp_api_secret IS 'TODO: Encrypt in production using pgcrypto';

-- ============================================================================
-- TABLE: credit_transactions
-- Purpose: Audit log of all credit purchases and usage
-- ============================================================================

CREATE TABLE IF NOT EXISTS credit_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  amount INTEGER NOT NULL,
  transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'refund', 'grant')),
  agent_name TEXT,
  agent_execution_id UUID,
  stripe_payment_id TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_workspace ON credit_transactions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_type ON credit_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created ON credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_execution ON credit_transactions(agent_execution_id);

COMMENT ON TABLE credit_transactions IS 'Audit log of credits: positive=purchase, negative=usage';
COMMENT ON COLUMN credit_transactions.amount IS 'Positive for purchases/grants, negative for usage';
COMMENT ON COLUMN credit_transactions.agent_name IS 'NULL for purchases, agent name for usage';

-- ============================================================================
-- TABLE: agent_executions
-- Purpose: Complete audit log of all agent executions
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_name TEXT NOT NULL,
  credits_charged INTEGER NOT NULL CHECK (credits_charged > 0),
  status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
  input_data JSONB,
  output_data JSONB,
  error_message TEXT,
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  duration_seconds INTEGER GENERATED ALWAYS AS (
    EXTRACT(EPOCH FROM (completed_at - started_at))::INTEGER
  ) STORED
);

CREATE INDEX IF NOT EXISTS idx_agent_executions_workspace ON agent_executions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_started ON agent_executions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent ON agent_executions(agent_name);

COMMENT ON TABLE agent_executions IS 'Audit log of all agent executions across workspaces';
COMMENT ON COLUMN agent_executions.duration_seconds IS 'Auto-calculated from completed_at - started_at';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at for workspaces
CREATE TRIGGER update_workspaces_updated_at
    BEFORE UPDATE ON workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Auto-update updated_at for optimizely_credentials
CREATE TRIGGER update_credentials_updated_at
    BEFORE UPDATE ON optimizely_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- View: Workspace summary with usage stats
CREATE OR REPLACE VIEW workspace_summary AS
SELECT
    w.id,
    w.name,
    w.email,
    w.credits_remaining,
    w.created_at,
    COUNT(DISTINCT ae.id) AS total_executions,
    COUNT(DISTINCT CASE WHEN ae.status = 'completed' THEN ae.id END) AS successful_executions,
    COUNT(DISTINCT CASE WHEN ae.status = 'failed' THEN ae.id END) AS failed_executions,
    COALESCE(SUM(CASE WHEN ct.transaction_type = 'purchase' THEN ct.amount ELSE 0 END), 0) AS total_credits_purchased,
    COALESCE(SUM(CASE WHEN ct.transaction_type = 'usage' THEN ABS(ct.amount) ELSE 0 END), 0) AS total_credits_used,
    MAX(ae.started_at) AS last_execution_at
FROM workspaces w
LEFT JOIN agent_executions ae ON w.id = ae.workspace_id
LEFT JOIN credit_transactions ct ON w.id = ct.workspace_id
GROUP BY w.id, w.name, w.email, w.credits_remaining, w.created_at;

COMMENT ON VIEW workspace_summary IS 'Aggregated workspace stats for admin dashboard';

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert test workspace
INSERT INTO workspaces (name, email, api_key, credits_remaining)
VALUES (
    'Test Agency',
    'test@jaxondigital.com',
    'jax_test_' || substring(md5(random()::text) from 1 for 24),
    1000
)
ON CONFLICT (email) DO NOTHING;

-- Insert test credentials (using Cambro as example)
INSERT INTO optimizely_credentials (workspace_id, project_name, dxp_api_key, dxp_api_secret, slack_webhook_url)
SELECT
    id,
    'cambro',
    'test_api_key',
    'test_api_secret',
    'https://hooks.slack.com/services/TEST/TEST/TEST'
FROM workspaces
WHERE email = 'test@jaxondigital.com'
ON CONFLICT (workspace_id, project_name) DO NOTHING;

-- Grant initial credits to test workspace
INSERT INTO credit_transactions (workspace_id, amount, transaction_type, metadata)
SELECT
    id,
    1000,
    'grant',
    '{"reason": "Initial test credits", "granted_by": "system"}'::jsonb
FROM workspaces
WHERE email = 'test@jaxondigital.com';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Query: Check schema creation
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE tablename IN ('workspaces', 'optimizely_credentials', 'credit_transactions', 'agent_executions')
ORDER BY tablename;

-- Query: Check test workspace
SELECT
    w.name,
    w.email,
    w.api_key,
    w.credits_remaining,
    COUNT(c.id) AS credentials_count
FROM workspaces w
LEFT JOIN optimizely_credentials c ON w.id = c.workspace_id
WHERE w.email = 'test@jaxondigital.com'
GROUP BY w.id, w.name, w.email, w.api_key, w.credits_remaining;

-- ============================================================================
-- GRANT PERMISSIONS (adjust based on your user setup)
-- ============================================================================

-- Grant all privileges to orchestrator user (adjust username as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO orchestrator;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO orchestrator;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO orchestrator;
