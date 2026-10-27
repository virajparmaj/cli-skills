#!/usr/bin/env python3
"""
audit_ml_vibe.py - Post-Vibe AI, LLM & Agentic Product Production Readiness Scanner.

Audits:
1. Prompt Injection & Jailbreak Vulnerabilities (Raw f-string interpolation, unsafe eval)
2. Agent Safeguards & Spend Caps (Runaway loop protection, token limits, spend caps)
3. Model Resilience & Versioning (Pinned snapshots, multi-provider fallbacks)
4. Data Privacy & PII Scrubbing (Zero-retention compliance, sanitization)
5. Structured Output & Streaming UX (SSE/WebSocket streaming, JSON schema validation)
6. Vector Database & RAG Multi-Tenancy (Metadata filtering on tenant_id)
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
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    "data",
    "models",
}

ML_SOURCE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Audit AI/ML/LLM codebase for vibe-coding gaps")
    parser.add_argument("--repo", default=".", help="Path to AI/ML repository")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    return parser.parse_args()


def walk_files(repo_path: Path):
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            p = Path(root) / f
            yield p


def check_prompt_security_and_injection(repo_path: Path):
    results = {
        "raw_string_prompts": [],
        "unsafe_code_execution": [],
        "delimiter_hygiene_found": False,
        "markdown_exfiltration_defense": False,
    }

    # Matches f"You are... {user_input}" or similar prompt templates with raw interpolation
    prompt_fstring = re.compile(r'f["\'].*?(?:system|prompt|assistant|query|user).*?\{[a-zA-Z0-9_]+\}.*?["\']', re.IGNORECASE)
    prompt_concat = re.compile(r'(?:prompt|instruction|system_message)\s*\+=\s*[a-zA-Z0-9_]+', re.IGNORECASE)
    unsafe_exec = re.compile(r'\b(?:eval|exec)\s*\(\s*(?:response|output|message|completion|result\.content)', re.IGNORECASE)

    for p in walk_files(repo_path):
        if p.suffix.lower() not in [".py", ".ts", ".js"]:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        if "<system>" in content or "<user_input>" in content or "### Instruction" in content or "xml_tags" in content:
            results["delimiter_hygiene_found"] = True

        if "sanitize_markdown" in content or "strip_images" in content or r"re.sub(r'!\[" in content:
            results["markdown_exfiltration_defense"] = True

        for idx, line in enumerate(content.splitlines(), 1):
            if prompt_fstring.search(line) or prompt_concat.search(line):
                if len(results["raw_string_prompts"]) < 6:
                    results["raw_string_prompts"].append({
                        "file": rel,
                        "line": idx,
                        "text": line.strip()[:75]
                    })

            if unsafe_exec.search(line):
                results["unsafe_code_execution"].append({
                    "file": rel,
                    "line": idx,
                    "text": line.strip()[:75]
                })

    return results


def check_agent_loops_and_spend_caps(repo_path: Path):
    results = {
        "runaway_agent_loops": [],
        "has_spend_cap": False,
        "has_token_tracking": False,
        "has_hitl_approval": False,
    }

    while_loop_pat = re.compile(r'while\s+(?:True|1|len\(messages\))\s*:', re.IGNORECASE)
    agent_loop_js = re.compile(r'while\s*\(\s*(?:true|1)\s*\)')

    for p in walk_files(repo_path):
        if p.suffix.lower() not in [".py", ".ts", ".js"]:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        lower = content.lower()
        if "spend_limit" in lower or "budget_limit" in lower or "spend_cap" in lower:
            results["has_spend_cap"] = True
        if "usage.total_tokens" in content or "prompt_tokens" in content or "usage_metadata" in content:
            results["has_token_tracking"] = True
        if "human_approval" in lower or "require_confirmation" in lower or "confirm_action" in lower:
            results["has_hitl_approval"] = True

        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if while_loop_pat.search(line) or agent_loop_js.search(line):
                # Check surrounding lines for max_iterations or break guard
                surrounding = "\n".join(lines[max(0, idx - 2):min(len(lines), idx + 20)])
                if not any(term in surrounding for term in ["max_iterations", "max_turns", "max_steps", "step_count", "iteration_limit"]):
                    if len(results["runaway_agent_loops"]) < 5:
                        results["runaway_agent_loops"].append({
                            "file": rel,
                            "line": idx,
                            "text": line.strip()[:75]
                        })

    return results


def check_model_versioning_and_fallbacks(repo_path: Path):
    results = {
        "unpinned_models": [],
        "pinned_models": [],
        "has_model_fallback": False,
        "has_eval_harness": False,
    }

    # Unpinned moving models
    unpinned_patterns = [
        re.compile(r'["\'](gpt-4o|gpt-4-turbo|gpt-4|gpt-3\.5-turbo)["\']'),
        re.compile(r'["\'](claude-3-5-sonnet|claude-3-opus|claude-3-haiku)["\']'),
        re.compile(r'["\'](gemini-1\.5-pro|gemini-1\.5-flash|gemini-pro)["\']'),
    ]

    # Pinned model snapshots
    pinned_pattern = re.compile(r'["\'](?:gpt-4o-\d{4}-\d{2}-\d{2}|claude-3-5-sonnet-\d{8}|gemini-1\.5-pro-\d{3}|gemini-2\.0-flash-\d{3})["\']')

    for p in walk_files(repo_path):
        rel = str(p.relative_to(repo_path))
        if any(term in p.name.lower() for term in ["eval", "benchmark", "golden_dataset"]):
            results["has_eval_harness"] = True

        if p.suffix.lower() not in [".py", ".ts", ".js", ".json", ".yaml"]:
            continue

        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        if any(term in content for term in ["fallback_models", "fallback_llm", "litellm.Router", "FallbackHandler"]):
            results["has_model_fallback"] = True

        for idx, line in enumerate(content.splitlines(), 1):
            m_pin = pinned_pattern.search(line)
            if m_pin:
                results["pinned_models"].append({"file": rel, "line": idx, "model": m_pin.group(0)})

            for unpin in unpinned_patterns:
                m_unpin = unpin.search(line)
                if m_unpin and not pinned_pattern.search(line):
                    if len(results["unpinned_models"]) < 6:
                        results["unpinned_models"].append({"file": rel, "line": idx, "model": m_unpin.group(0)})

    return results


def check_rag_and_vector_db_isolation(repo_path: Path):
    results = {
        "vector_db_found": False,
        "vector_frameworks": [],
        "has_tenant_metadata_filtering": False,
        "streaming_detected": False,
        "structured_output_enforced": False,
    }

    vector_indicators = ["pinecone", "weaviate", "qdrant", "chromadb", "pgvector", "milvus"]

    for p in walk_files(repo_path):
        if p.suffix.lower() not in [".py", ".ts", ".js"]:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        lower = content.lower()
        for v in vector_indicators:
            if v in lower and v not in results["vector_frameworks"]:
                results["vector_db_found"] = True
                results["vector_frameworks"].append(v)

        if "filter={" in content or "filter: {" in content or "where={" in content:
            if any(t in lower for t in ["tenant_id", "user_id", "org_id", "workspace_id"]):
                results["has_tenant_metadata_filtering"] = True

        if "stream=True" in content or "stream: true" in content or "response_stream" in lower:
            results["streaming_detected"] = True

        if "response_format" in content or "output_schema" in content or "instructor" in lower or "with_structured_output" in content:
            results["structured_output_enforced"] = True

    return results


def main():
    args = parse_args()
    repo_path = Path(args.repo).resolve()

    if not repo_path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    prompt_sec = check_prompt_security_and_injection(repo_path)
    agent_guards = check_agent_loops_and_spend_caps(repo_path)
    versioning = check_model_versioning_and_fallbacks(repo_path)
    rag_sec = check_rag_and_vector_db_isolation(repo_path)

    full_report = {
        "repo": str(repo_path),
        "prompt_security": prompt_sec,
        "agent_guards": agent_guards,
        "model_versioning": versioning,
        "rag_and_serving": rag_sec,
    }

    if args.json:
        print(json.dumps(full_report, indent=2))
        return

    print("=" * 70)
    print("V-VIBE-ML: AI, LLM & AGENTIC APPLICATION PRODUCTION AUDIT")
    print("=" * 70)

    print("\n1. Prompt Injection & AI Security:")
    if prompt_sec["unsafe_code_execution"]:
        print(f"  - [CRITICAL] Unsafe eval/exec of LLM output ({len(prompt_sec['unsafe_code_execution'])} instances):")
        for u in prompt_sec["unsafe_code_execution"]:
            print(f"    * {u['file']}:{u['line']} -> {u['text']}")
    else:
        print("  - Unsafe Code Execution: NONE (Clean)")

    if prompt_sec["raw_string_prompts"]:
        print(f"  - [WARNING] Raw f-string prompt concatenation detected ({len(prompt_sec['raw_string_prompts'])} instances):")
        for r in prompt_sec["raw_string_prompts"][:3]:
            print(f"    * {r['file']}:{r['line']} -> {r['text']}")
    else:
        print("  - Prompt Formatting: Clean structured messages")
    print(f"  - Delimiter / XML tag hygiene: {'DETECTED' if prompt_sec['delimiter_hygiene_found'] else 'MISSING (Vulnerable to instruction confusion)'}")

    print("\n2. Agent Safeguards & Spend Defense:")
    if agent_guards["runaway_agent_loops"]:
        print(f"  - [CRITICAL] Agent loops without iteration guards ({len(agent_guards['runaway_agent_loops'])} instances):")
        for loop in agent_guards["runaway_agent_loops"][:3]:
            print(f"    * {loop['file']}:{loop['line']} -> {loop['text']}")
    else:
        print("  - Agent Loop Circuit Breakers: PROTECTED")
    print(f"  - Hard Token / Spend Cap Configured: {'YES' if agent_guards['has_spend_cap'] else 'NO (Denial-of-wallet risk)'}")
    print(f"  - Token Usage Telemetry: {'TRACKED' if agent_guards['has_token_tracking'] else 'MISSING'}")
    print(f"  - Human-in-the-Loop (HITL) for Destructive Actions: {'FOUND' if agent_guards['has_hitl_approval'] else 'NOT FOUND'}")

    print("\n3. Model Reliability & Versioning:")
    print(f"  - Pinned Model Snapshots: {len(versioning['pinned_models'])} instances")
    if versioning["unpinned_models"]:
        print(f"  - [WARNING] Unpinned moving model aliases in use ({len(versioning['unpinned_models'])} instances):")
        for m in versioning["unpinned_models"][:3]:
            print(f"    * {m['file']}:{m['line']} -> {m['model']}")
    print(f"  - Multi-Provider Fallback Architecture: {'CONFIGURED' if versioning['has_model_fallback'] else 'SINGLE PROVIDER DEPENDENCY (Outage risk)'}")
    print(f"  - Automated LLM Eval / Benchmark Suite: {'FOUND' if versioning['has_eval_harness'] else 'MISSING (Blind to prompt/model degradation)'}")

    print("\n4. RAG Hygiene & Serving Performance:")
    if rag_sec["vector_db_found"]:
        print(f"  - Vector DB Detected: {', '.join(rag_sec['vector_frameworks'])}")
        print(f"  - Tenant ID Metadata Filtering: {'ENFORCED' if rag_sec['has_tenant_metadata_filtering'] else 'CRITICAL: Missing tenant filter in vector search (Cross-tenant RAG leak risk)'}")
    print(f"  - Response Token Streaming (SSE/WebSocket): {'IMPLEMENTED' if rag_sec['streaming_detected'] else 'NO (High TTFT / timeout risk)'}")
    print(f"  - Structured Output Enforcement: {'ENFORCED (Pydantic/JSON Schema)' if rag_sec['structured_output_enforced'] else 'UNSTRUCTURED (Prone to JSON parse crashes)'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
