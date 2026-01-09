# HashiCorp Vault Configuration for AI Agents
# Implements just-in-time privileged access for autonomous agents

# Storage backend configuration
storage "file" {
  path = "/vault/data"
}

# Listener configuration
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 0
  tls_cert_file = "/vault/tls/vault.crt"
  tls_key_file  = "/vault/tls/vault.key"
}

# API address
api_addr = "https://vault.evolving-sun.ai:8200"
cluster_addr = "https://vault.evolving-sun.ai:8201"

# UI configuration
ui = true

# Telemetry
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = false
}

# Agent-specific secret paths
path "secret/agents/*" {
  capabilities = ["read", "list"]
  
  # Just-in-time access
  min_wrapping_ttl = "5m"
  max_wrapping_ttl = "1h"
  
  # Agent-specific policies
  allowed_parameters {
    agent_id = []
    confidence_score = ["0.85-1.0"]
    task_context = []
  }
  
  # Deny conditions
  denied_parameters {
    confidence_score = ["0.0-0.84"]
  }
}

# API keys with automatic rotation
path "secret/api-keys/*" {
  capabilities = ["read"]
  
  # Short-lived credentials
  ttl = "30m"
  max_ttl = "1h"
  
  # Automatic rotation
  rotation {
    enabled = true
    period = "24h"
    auto_rotate = true
  }
}

# Database credentials (dynamic)
path "database/creds/ai-agents" {
  capabilities = ["read"]
  
  # Dynamic credentials
  ttl = "1h"
  max_ttl = "4h"
  
  # Automatic cleanup
  revocation_enabled = true
}

# Production secrets (high security)
path "secret/production/*" {
  capabilities = ["read"]
  
  # Strict access control
  min_wrapping_ttl = "5m"
  max_wrapping_ttl = "15m"
  
  # Require high confidence
  allowed_parameters {
    confidence_score = ["0.95-1.0"]
    human_approved = ["true"]
  }
  
  # MFA requirement
  mfa_methods = ["totp", "duo"]
}

# LLM provider API keys
path "secret/llm-providers/*" {
  capabilities = ["read"]
  
  # Provider-specific TTLs
  ttl = "1h"
  max_ttl = "24h"
  
  # Rate limiting
  rate_limit {
    rate = "10"
    burst = "15"
  }
}

# Encryption keys
path "transit/encrypt/agent-data" {
  capabilities = ["update"]
  
  # Transit encryption
  allowed_parameters {
    plaintext = []
    context = []
  }
}

path "transit/decrypt/agent-data" {
  capabilities = ["update"]
  
  allowed_parameters {
    ciphertext = []
    context = []
  }
}

# Audit logging (immutable)
audit {
  type = "file"
  description = "Agent secrets access log"
  
  options {
    file_path = "/var/log/vault/agent-audit.log"
    log_raw = true
    hmac_accessor = false
    format = "json"
  }
  
  # Retention and integrity
  retention = "2555d"  # 7 years
  integrity_check = "sha256"
}

# Additional audit backend for redundancy
audit {
  type = "syslog"
  description = "Syslog audit backend"
  
  options {
    facility = "AUTH"
    tag = "vault-agents"
  }
}

# Policy definitions

# Security Agent Policy
path "secret/security-agent/*" {
  capabilities = ["read", "list"]
  
  allowed_parameters {
    scan_type = ["vulnerability", "secret", "dependency"]
  }
}

# Quality Agent Policy
path "secret/quality-agent/*" {
  capabilities = ["read", "list"]
  
  allowed_parameters {
    action = ["lint", "test", "coverage"]
  }
}

# Documentation Agent Policy
path "secret/documentation-agent/*" {
  capabilities = ["read", "list"]
  
  allowed_parameters {
    doc_type = ["api", "readme", "changelog"]
  }
}

# Benchmark Agent Policy
path "secret/benchmark-agent/*" {
  capabilities = ["read", "list"]
  
  allowed_parameters {
    benchmark = ["gpqa", "swe-bench", "kegg"]
  }
}

# Triage Agent Policy
path "secret/triage-agent/*" {
  capabilities = ["read", "list"]
  
  allowed_parameters {
    action = ["label", "assign", "close"]
  }
}

# Optimization Agent Policy
path "secret/optimization-agent/*" {
  capabilities = ["read", "list"]
  
  allowed_parameters {
    optimize_for = ["cost", "latency", "accuracy"]
  }
}

# Token helper configuration
# token_helper = "/usr/local/bin/vault-token-helper"

# Plugin directory
plugin_directory = "/vault/plugins"

# Maximum request duration
max_lease_ttl = "768h"  # 32 days
default_lease_ttl = "24h"

# Disable mlock for development (enable in production)
# disable_mlock = true

# Log level
log_level = "info"

# Performance tuning
max_request_size = 33554432  # 32MB
disable_cache = false
