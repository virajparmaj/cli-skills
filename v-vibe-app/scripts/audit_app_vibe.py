#!/usr/bin/env python3
"""
audit_app_vibe.py - Post-Vibe Full-Stack SaaS, Backend & Distributed Systems Scanner.

Audits:
1. 19 Distributed Systems Pillars (Rate limiting, Caching, Queues, Retries, Idempotency)
2. Database Hygiene (Migrations, Indexing, Connection pooling, Integer money, RLS)
3. Auth & Multi-Tenancy (Tenant isolation, IDOR, MFA, Session management)
4. Pre-Launch 20 Essentials (Secrets in code, Sentry tracking, Health endpoints, Webhooks)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".astro",
    "out",
    ".vercel",
    ".turbo",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    "tmp",
}

APP_SOURCE_SUFFIXES = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".py",
    ".go",
    ".rs",
    ".rb",
    ".java",
    ".sql",
    ".json",
    ".yaml",
    ".yml",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Audit application codebase for vibe-coding gaps")
    parser.add_argument("--repo", default=".", help="Path to SaaS application repository")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    return parser.parse_args()


def walk_files(repo_path: Path):
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            p = Path(root) / f
            yield p


def check_secrets_and_env(repo_path: Path):
    results = {
        "hardcoded_secrets": [],
        "env_example_found": False,
        "env_files_in_git": [],
    }

    secret_patterns = [
        ("Stripe Secret Key", re.compile(r'sk_live_[0-9a-zA-Z]{24,}')),
        ("AWS Access Key", re.compile(r'AKIA[0-9A-Z]{16}')),
        ("Generic Private Key", re.compile(r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----')),
        ("Supabase Service Role", re.compile(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]{30,}\.[a-zA-Z0-9_-]{30,}')),
        ("Hardcoded Password in URL", re.compile(r'postgres(?:ql)?:\/\/[^:]+:([^@]+)@')),
    ]

    for p in walk_files(repo_path):
        rel = str(p.relative_to(repo_path))
        if p.name == ".env.example":
            results["env_example_found"] = True
        if p.name in [".env", ".env.production", ".env.local"] and not p.name.endswith(".example"):
            results["env_files_in_git"].append(rel)

        if p.suffix.lower() not in APP_SOURCE_SUFFIXES or p.name.startswith(".env"):
            continue

        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if any(term in line.lower() for term in ["dummy", "mock", "test", "example", "placeholder"]):
                continue
            for name, pattern in secret_patterns:
                if pattern.search(line):
                    results["hardcoded_secrets"].append({
                        "file": rel,
                        "line": idx,
                        "type": name,
                        "preview": line.strip()[:80]
                    })
                    break

    return results


def check_distributed_systems_pillars(repo_path: Path):
    results = {
        "rate_limiting": {"found": False, "files": []},
        "caching": {"found": False, "files": []},
        "message_queues": {"found": False, "files": []},
        "idempotency": {"found": False, "files": []},
        "circuit_breaker": {"found": False, "files": []},
        "timeouts_configured": {"found": False, "files": []},
        "retries_and_backoff": {"found": False, "files": []},
    }

    patterns = {
        "rate_limiting": re.compile(r'(express-rate-limit|ratelimit|slowapi|throttle|rate_limit|sliding_window)', re.IGNORECASE),
        "caching": re.compile(r'(ioredis|redis|memcached|cache-aside|cache_page|stale-while-revalidate)', re.IGNORECASE),
        "message_queues": re.compile(r'(bullmq|bull|celery|rabbitmq|amqp|sqs|kafka|sidekiq)', re.IGNORECASE),
        "idempotency": re.compile(r'(idempotency-key|idempotency_key|idempotent|x-idempotency)', re.IGNORECASE),
        "circuit_breaker": re.compile(r'(circuitbreaker|opossum|pybreaker|resilience4j)', re.IGNORECASE),
        "timeouts_configured": re.compile(r'(timeout\s*:\s*\d+|timeout\s*=\s*\d+|timeout_seconds)', re.IGNORECASE),
        "retries_and_backoff": re.compile(r'(exponential_backoff|backoff|retry_delay|max_retries|p-retry)', re.IGNORECASE),
    }

    for p in walk_files(repo_path):
        if p.suffix.lower() not in APP_SOURCE_SUFFIXES:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        for key, pat in patterns.items():
            if pat.search(content):
                results[key]["found"] = True
                if len(results[key]["files"]) < 5:
                    results[key]["files"].append(rel)

    return results


def check_database_hygiene(repo_path: Path):
    results = {
        "has_migrations": False,
        "migration_framework": None,
        "float_money_fields": [],
        "has_connection_pooling": False,
        "soft_delete_support": False,
        "rls_enabled": False,
    }

    # Check migration directories
    if list(repo_path.glob("**/prisma/schema.prisma")):
        results["has_migrations"] = True
        results["migration_framework"] = "Prisma"
    elif list(repo_path.glob("**/supabase/migrations/*.sql")):
        results["has_migrations"] = True
        results["migration_framework"] = "Supabase"
    elif list(repo_path.glob("**/drizzle/*.ts")) or list(repo_path.glob("**/drizzle.config.*")):
        results["has_migrations"] = True
        results["migration_framework"] = "Drizzle"
    elif list(repo_path.glob("**/alembic/versions/*.py")) or list(repo_path.glob("**/alembic.ini")):
        results["has_migrations"] = True
        results["migration_framework"] = "Alembic"
    elif list(repo_path.glob("**/migrations/*.py")):
        results["has_migrations"] = True
        results["migration_framework"] = "Django"

    float_money_pat = re.compile(r'(price|amount|balance|fee|cost|total|salary)\s*:\s*(?:number|float|Double|Float)', re.IGNORECASE)
    pg_float_money = re.compile(r'(price|amount|balance|fee|cost|total)\s+(?:FLOAT|REAL|DOUBLE PRECISION)', re.IGNORECASE)

    for p in walk_files(repo_path):
        if p.suffix.lower() not in APP_SOURCE_SUFFIXES:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        if "pgbouncer" in content.lower() or "pool_size" in content or "connection_limit" in content:
            results["has_connection_pooling"] = True

        if "deleted_at" in content or "deletedAt" in content or "softdelete" in content.lower():
            results["soft_delete_support"] = True

        if "enable row level security" in content.lower():
            results["rls_enabled"] = True

        # Scan for float money
        for idx, line in enumerate(content.splitlines(), 1):
            if float_money_pat.search(line) or pg_float_money.search(line):
                if len(results["float_money_fields"]) < 8:
                    results["float_money_fields"].append({
                        "file": rel,
                        "line": idx,
                        "text": line.strip()[:70]
                    })

    return results


def check_auth_and_security(repo_path: Path):
    results = {
        "mfa_references": False,
        "sso_saml_references": False,
        "scim_references": False,
        "rbac_detected": False,
        "tenant_id_found": False,
        "leaking_stack_traces": [],
        "webhook_signature_verified": False,
        "error_tracking_found": False,
    }

    for p in walk_files(repo_path):
        if p.suffix.lower() not in APP_SOURCE_SUFFIXES:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        lower = content.lower()
        if "mfa" in lower or "totp" in lower or "two_factor" in lower:
            results["mfa_references"] = True
        if "saml" in lower or "sso" in lower or "workos" in lower or "auth0" in lower:
            results["sso_saml_references"] = True
        if "scim" in lower:
            results["scim_references"] = True
        if "role" in lower and any(r in lower for r in ["permission", "scope", "can(", "haspermission"]):
            results["rbac_detected"] = True
        if "tenant_id" in lower or "tenantid" in lower or "organization_id" in lower or "org_id" in lower:
            results["tenant_id_found"] = True
        if "sentry" in lower or "bugsnag" in lower or "highlight.io" in lower:
            results["error_tracking_found"] = True
        if "constructevent" in content or "verify_signature" in lower or "webhook_secret" in lower:
            results["webhook_signature_verified"] = True

        # Check stack trace leak
        if "err.stack" in content or "traceback.format_exc()" in content:
            if "res.send" in content or "res.json" in content or "Response(" in content:
                results["leaking_stack_traces"].append(rel)

    return results


def check_codebase_and_design_slop(repo_path: Path):
    results = {
        "codebase_slop": {
            "layer_first_layout": False,
            "feature_first_layout": False,
            "god_files": [],
            "representable_illegal_states": [],
            "layering_violations": [],
            "boundary_validation_found": False,
        },
        "design_slop": {
            "badge_count": 0,
            "divider_count": 0,
            "italic_buzzwords": [],
            "instrument_serif_negative_kerning": [],
            "bordered_container_count": 0,
            "section_numbering": [],
            "code_breadcrumbs": [],
        },
    }

    # Check directory layout
    for base in [repo_path / "src", repo_path / "backend", repo_path / "api", repo_path / "app"]:
        if base.exists() and base.is_dir():
            layer_dirs = {"controllers", "services", "models", "routes", "views", "components", "utils"}
            found = [d.name for d in base.iterdir() if d.is_dir() and d.name in layer_dirs]
            has_features = (base / "features").is_dir() or (base / "modules").is_dir() or (base / "domains").is_dir()
            if len(found) >= 3 and not has_features:
                results["codebase_slop"]["layer_first_layout"] = True
            if has_features:
                results["codebase_slop"]["feature_first_layout"] = True

    illegal_state_pat = re.compile(r'(?:isLoading|loading)\s*:\s*boolean.*?(?:isError|error).*?(?:data|user)', re.DOTALL)
    layering_violation_pat = re.compile(r'(?:supabase\.from\(|prisma\.[a-zA-Z0-9_]+\.(?:find|create|update)|SELECT\s+.+?\s+FROM)', re.IGNORECASE)
    validation_pat = re.compile(r'(?:z\.object|BaseModel|class-validator|joi\.object|yup\.object)')
    badge_pat = re.compile(r'<Badge\b')
    divider_pat = re.compile(r'(?:<Separator\b|<hr\b|divide-y|border-t\b)')
    italic_pat = re.compile(r'(?:\*(?:effortlessly|seamlessly|intelligently|instantly|automatically)\*|\bitalic\b)', re.IGNORECASE)
    serif_kerning_pat = re.compile(r'(?:font-serif|Instrument Serif).*?(?:tracking-tighter|tracking-\[-0\.05em\])', re.IGNORECASE)
    border_container_pat = re.compile(r'border\s+border-border\s+rounded-')
    section_num_pat = re.compile(r'(?:0[1-9]\s*\/|0[1-9]\s*-\s*|Step\s*0?[1-9][:\s-])', re.IGNORECASE)
    breadcrumb_pat = re.compile(r'(?:Dashboard\s*>\s*[A-Za-z]+|[A-Za-z]+\s*>\s*[A-Za-z]+\s*>\s*[A-Za-z]+)')

    for p in walk_files(repo_path):
        if p.suffix.lower() not in APP_SOURCE_SUFFIXES:
            continue
        rel = str(p.relative_to(repo_path))

        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        lines = content.splitlines()
        if len(lines) > 300 and len(results["codebase_slop"]["god_files"]) < 5:
            results["codebase_slop"]["god_files"].append({"file": rel, "lines": len(lines)})

        if illegal_state_pat.search(content) and len(results["codebase_slop"]["representable_illegal_states"]) < 3:
            results["codebase_slop"]["representable_illegal_states"].append(rel)

        if validation_pat.search(content):
            results["codebase_slop"]["boundary_validation_found"] = True

        is_ui = any(part in ["components", "views", "pages", "app"] for part in p.parts) or p.suffix.lower() in [".tsx", ".jsx"]
        if is_ui:
            if layering_violation_pat.search(content) and len(results["codebase_slop"]["layering_violations"]) < 3:
                results["codebase_slop"]["layering_violations"].append(rel)

            results["design_slop"]["badge_count"] += len(badge_pat.findall(content))
            results["design_slop"]["divider_count"] += len(divider_pat.findall(content))
            results["design_slop"]["bordered_container_count"] += len(border_container_pat.findall(content))

            for m in italic_pat.finditer(content):
                if len(results["design_slop"]["italic_buzzwords"]) < 3:
                    results["design_slop"]["italic_buzzwords"].append({"file": rel, "text": m.group(0)})

            for m in serif_kerning_pat.finditer(content):
                if len(results["design_slop"]["instrument_serif_negative_kerning"]) < 3:
                    results["design_slop"]["instrument_serif_negative_kerning"].append({"file": rel, "text": m.group(0)})

            for m in section_num_pat.finditer(content):
                if len(results["design_slop"]["section_numbering"]) < 3:
                    results["design_slop"]["section_numbering"].append({"file": rel, "text": m.group(0)})

            for m in breadcrumb_pat.finditer(content):
                if len(results["design_slop"]["code_breadcrumbs"]) < 3:
                    results["design_slop"]["code_breadcrumbs"].append({"file": rel, "text": m.group(0)})

    return results


def main():
    args = parse_args()
    repo_path = Path(args.repo).resolve()

    if not repo_path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    secrets = check_secrets_and_env(repo_path)
    dist_systems = check_distributed_systems_pillars(repo_path)
    db = check_database_hygiene(repo_path)
    auth_sec = check_auth_and_security(repo_path)
    slop_report = check_codebase_and_design_slop(repo_path)

    full_report = {
        "repo": str(repo_path),
        "secrets": secrets,
        "distributed_systems": dist_systems,
        "database": db,
        "auth_and_security": auth_sec,
        "slop_audit": slop_report,
    }

    if args.json:
        print(json.dumps(full_report, indent=2))
        return

    print("=" * 70)
    print("V-VIBE-APP: FULL-STACK SAAS & BACKEND PRODUCTION AUDIT")
    print("=" * 70)

    print("\n1. Secrets & Environment Hygiene:")
    if secrets["hardcoded_secrets"]:
        print(f"  - [CRITICAL] Hardcoded secrets detected: {len(secrets['hardcoded_secrets'])}")
        for s in secrets["hardcoded_secrets"][:3]:
            print(f"    * {s['file']}:{s['line']} - {s['type']}")
    else:
        print("  - Hardcoded secrets: NONE DETECTED (Pass)")
    if secrets["env_files_in_git"]:
        print(f"  - [WARNING] Live .env files in git tree: {', '.join(secrets['env_files_in_git'])}")
    print(f"  - .env.example present: {'YES' if secrets['env_example_found'] else 'NO (Missing template)'}")

    print("\n2. Distributed Systems Pillars (The 19 Architectures):")
    for pillar in ["rate_limiting", "caching", "message_queues", "idempotency", "circuit_breaker", "timeouts_configured", "retries_and_backoff"]:
        status = "FOUND" if dist_systems[pillar]["found"] else "MISSING / UNVERIFIED"
        files_str = f" ({', '.join(dist_systems[pillar]['files'][:2])})" if dist_systems[pillar]["files"] else ""
        print(f"  - {pillar.replace('_', ' ').title()}: {status}{files_str}")

    print("\n3. Database & Data Integrity:")
    print(f"  - Database Migrations: {'YES (' + str(db['migration_framework']) + ')' if db['has_migrations'] else 'NO (Ad-hoc database risk)'}")
    print(f"  - Connection Pooling (PgBouncer/Pool): {'CONFIGURED' if db['has_connection_pooling'] else 'UNVERIFIED (Traffic spike exhaustion risk)'}")
    print(f"  - Soft Delete Pattern: {'DETECTED' if db['soft_delete_support'] else 'NO (Accidental deletion risk)'}")
    print(f"  - Row Level Security (RLS): {'ENABLED' if db['rls_enabled'] else 'NOT FOUND'}")
    if db["float_money_fields"]:
        print(f"  - [CRITICAL] Floating-point currency detected ({len(db['float_money_fields'])} instances):")
        for f in db["float_money_fields"][:3]:
            print(f"    * {f['file']}:{f['line']} -> {f['text']}")
    else:
        print("  - Integer/Decimal Money: PASS (No naive float money fields found)")

    print("\n4. Enterprise Auth & Multi-Tenancy:")
    print(f"  - Multi-Tenant Isolation (tenant_id): {'FOUND' if auth_sec['tenant_id_found'] else 'WARNING: Missing explicit tenant scoping'}")
    print(f"  - Granular RBAC: {'DETECTED' if auth_sec['rbac_detected'] else 'BINARY ADMIN / UNVERIFIED'}")
    print(f"  - MFA / 2FA Support: {'DETECTED' if auth_sec['mfa_references'] else 'NOT FOUND'}")
    print(f"  - SSO / SAML Enterprise Auth: {'DETECTED' if auth_sec['sso_saml_references'] else 'NOT FOUND'}")
    print(f"  - SCIM User Provisioning: {'DETECTED' if auth_sec['scim_references'] else 'NOT FOUND'}")
    print(f"  - Webhook Signature Verification: {'PASS' if auth_sec['webhook_signature_verified'] else 'FAIL (Unverified webhook caller)'}")
    print(f"  - Sentry / Error Monitoring: {'CONFIGURED' if auth_sec['error_tracking_found'] else 'MISSING (Blind to production crashes)'}")
    if auth_sec["leaking_stack_traces"]:
        print(f"  - [WARNING] Possible stack trace leakage to client: {', '.join(auth_sec['leaking_stack_traces'][:3])}")

    print("\n5. Codebase Slop Indicators (The 9 Core Antipatterns):")
    cs = slop_report["codebase_slop"]
    if cs["layer_first_layout"]:
        print("  - [WARNING] Layer-first folder structure (controllers/services/models without feature slices)")
    elif cs["feature_first_layout"]:
        print("  - Feature-first domain layout: PASS")
    if cs["god_files"]:
        print(f"  - [WARNING] God files (> 300 LOC) found ({len(cs['god_files'])} files):")
        for gf in cs["god_files"][:3]:
            print(f"    * {gf['file']} ({gf['lines']} lines)")
    if cs["representable_illegal_states"]:
        print(f"  - [WARNING] Representable illegal states in: {', '.join(cs['representable_illegal_states'][:3])}")
    if cs["layering_violations"]:
        print(f"  - [WARNING] Direct DB queries in UI components: {', '.join(cs['layering_violations'][:3])}")
    print(f"  - Boundary validation (Zod/Pydantic/Joi): {'FOUND' if cs['boundary_validation_found'] else 'NOT DETECTED AT INGRESS'}")

    print("\n6. Dashboard Design Slop Indicators:")
    ds = slop_report["design_slop"]
    print(f"  - Badge/Tag spam: {ds['badge_count']} instances")
    print(f"  - Divider lines (Separator/hr/border-t): {ds['divider_count']} instances")
    print(f"  - Nested bordered containers: {ds['bordered_container_count']}")
    if ds["italic_buzzwords"]:
        print(f"  - [WARNING] Italicized copy/buzzwords ({len(ds['italic_buzzwords'])} found):")
        for ib in ds["italic_buzzwords"][:3]:
            print(f"    * {ib['file']}: {ib['text']}")
    if ds["instrument_serif_negative_kerning"]:
        print(f"  - [WARNING] Serif font + negative kerning: {len(ds['instrument_serif_negative_kerning'])} found")
    if ds["section_numbering"]:
        print(f"  - Section numbering (01 /, Step 01): {len(ds['section_numbering'])} found")
    if ds["code_breadcrumbs"]:
        print(f"  - Code breadcrumbs / terminal mockups: {len(ds['code_breadcrumbs'])} found")
    print("=" * 70)


if __name__ == "__main__":
    main()
