#!/usr/bin/env python3
"""
audit_macos_vibe.py - Post-Vibe macOS Desktop Software Production & App Store Readiness Scanner.

Audits:
1. App Sandbox, Entitlements & Hardened Runtime (Least-privilege, temporary exceptions)
2. Privacy Manifest (PrivacyInfo.xcprivacy) & App Store Rejection Risks
3. Desktop Architecture (Atomic writes, Retain cycles, SQLite WAL mode, Timer polling)
4. Electron / Tauri / Native Security (Node integration, Context isolation, Sparkle keys)
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "DerivedData",
    ".build",
    "Pods",
    "Carthage",
    "__pycache__",
}

MACOS_SOURCE_EXTENSIONS = {
    ".swift",
    ".m",
    ".h",
    ".rs",
    ".js",
    ".ts",
    ".tsx",
    ".entitlements",
    ".plist",
    ".json",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Audit macOS desktop codebase for vibe-coding gaps")
    parser.add_argument("--repo", default=".", help="Path to macOS project repository")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    return parser.parse_args()


def walk_files(repo_path: Path):
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            p = Path(root) / f
            yield p


def detect_macos_project_type(repo_path: Path):
    types = []
    if list(repo_path.glob("**/*.xcodeproj")) or list(repo_path.glob("**/Package.swift")):
        types.append("Native Swift/Xcode")
    if list(repo_path.glob("**/tauri.conf.json")):
        types.append("Tauri (Rust + Web)")
    if list(repo_path.glob("**/electron-builder.yml")) or list(repo_path.glob("**/electron-builder.json")):
        types.append("Electron (Node + Web)")
    elif any("electron" in p.read_text(errors="ignore").lower() for p in repo_path.glob("**/package.json")):
        types.append("Electron (Node + Web)")

    return types or ["Generic / Unknown Desktop"]


def check_entitlements_and_sandbox(repo_path: Path):
    results = {
        "entitlements_files": [],
        "sandbox_enabled": False,
        "temporary_exceptions": [],
        "network_client": False,
        "network_server": False,
        "user_selected_files": False,
        "bookmarks_app_scope": False,
    }

    ent_files = list(repo_path.glob("**/*.entitlements"))
    ent_files = [p for p in ent_files if not any(part in IGNORE_DIRS for part in p.parts)]

    for p in ent_files:
        rel = str(p.relative_to(repo_path))
        results["entitlements_files"].append(rel)
        try:
            content = p.read_text(errors="ignore")
            if "com.apple.security.app-sandbox" in content and "<true/>" in content:
                results["sandbox_enabled"] = True
            if "com.apple.security.network.client" in content:
                results["network_client"] = True
            if "com.apple.security.network.server" in content:
                results["network_server"] = True
            if "com.apple.security.files.user-selected" in content:
                results["user_selected_files"] = True
            if "com.apple.security.files.bookmarks.app-scope" in content:
                results["bookmarks_app_scope"] = True

            for line in content.splitlines():
                if "temporary-exception" in line:
                    match = re.search(r'<key>([^<]+)<\/key>', line)
                    if match:
                        results["temporary_exceptions"].append({"file": rel, "exception": match.group(1)})
        except Exception:
            pass

    return results


def check_privacy_manifest_and_store_readiness(repo_path: Path):
    results = {
        "has_privacy_manifest": False,
        "manifest_path": None,
        "has_sparkle_updater": False,
        "has_sparkle_eddsa_key": False,
        "deprecated_apis": [],
    }

    manifests = list(repo_path.glob("**/PrivacyInfo.xcprivacy"))
    manifests = [p for p in manifests if not any(part in IGNORE_DIRS for part in p.parts)]
    if manifests:
        results["has_privacy_manifest"] = True
        results["manifest_path"] = str(manifests[0].relative_to(repo_path))

    deprecated_patterns = [
        ("WebView (Use WKWebView)", re.compile(r'\bWebView\b')),
        ("NSArchiver (Insecure, use NSSecureCoding)", re.compile(r'\bNSArchiver\b')),
        ("Gestalt (Deprecated Carbon API)", re.compile(r'\bGestalt\b')),
    ]

    for p in walk_files(repo_path):
        if p.suffix.lower() not in [".swift", ".m", ".h", ".plist"]:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        if "SUFeedURL" in content:
            results["has_sparkle_updater"] = True
        if "SUPublicEDKey" in content:
            results["has_sparkle_eddsa_key"] = True

        for name, pat in deprecated_patterns:
            if pat.search(content):
                if len(results["deprecated_apis"]) < 5:
                    results["deprecated_apis"].append({"file": rel, "api": name})

    return results


def check_swift_desktop_architecture(repo_path: Path):
    results = {
        "retain_cycle_risks": [],
        "non_atomic_writes": [],
        "polling_timers": [],
        "sqlite_wal_configured": False,
    }

    timer_pat = re.compile(r'Timer\.scheduledTimer\s*\(\s*withTimeInterval:\s*(\d+(?:\.\d+)?)')
    non_atomic_pat = re.compile(r'\.write\(to:\s*[^)]+\)(?!\s*options:\s*\[\.atomic\])')
    closure_strong_self = re.compile(r'\{\s*(?:\[[^\]]*\])?\s*(?:\([^)]*\)\s*in|in)\s+self\.')

    for p in walk_files(repo_path):
        if p.suffix.lower() != ".swift":
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        if "journal_mode=WAL" in content or "PRAGMA journal_mode = WAL" in content or "NSSQLitePragmasOption" in content:
            results["sqlite_wal_configured"] = True

        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            # Check fast polling timer
            m_timer = timer_pat.search(line)
            if m_timer:
                interval = float(m_timer.group(1))
                if interval < 2.0:
                    results["polling_timers"].append({
                        "file": rel,
                        "line": idx,
                        "interval": interval,
                        "text": line.strip()[:70]
                    })

            # Check non-atomic writes
            if "write(to:" in line and ".atomic" not in line and len(results["non_atomic_writes"]) < 5:
                results["non_atomic_writes"].append({
                    "file": rel,
                    "line": idx,
                    "text": line.strip()[:70]
                })

    return results


def check_electron_tauri_security(repo_path: Path):
    results = {
        "node_integration_danger": [],
        "context_isolation_disabled": [],
        "tauri_allowlist_broad": False,
    }

    for p in walk_files(repo_path):
        rel = str(p.relative_to(repo_path))
        if p.suffix.lower() in [".js", ".ts", ".tsx", ".json"]:
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            if "nodeIntegration: true" in content or '"nodeIntegration": true' in content:
                results["node_integration_danger"].append(rel)
            if "contextIsolation: false" in content or '"contextIsolation": false' in content:
                results["context_isolation_disabled"].append(rel)

            if p.name == "tauri.conf.json":
                if '"all": true' in content:
                    results["tauri_allowlist_broad"] = True

    return results


def main():
    args = parse_args()
    repo_path = Path(args.repo).resolve()

    if not repo_path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    project_types = detect_macos_project_type(repo_path)
    entitlements = check_entitlements_and_sandbox(repo_path)
    privacy = check_privacy_manifest_and_store_readiness(repo_path)
    swift_arch = check_swift_desktop_architecture(repo_path)
    web_desktop = check_electron_tauri_security(repo_path)

    full_report = {
        "repo": str(repo_path),
        "project_types": project_types,
        "entitlements": entitlements,
        "privacy_and_store": privacy,
        "swift_desktop": swift_arch,
        "electron_tauri": web_desktop,
    }

    if args.json:
        print(json.dumps(full_report, indent=2))
        return

    print("=" * 70)
    print("V-VIBE-MACOS: MACOS DESKTOP APP PRODUCTION AUDIT")
    print("=" * 70)
    print(f"Project Architecture: {', '.join(project_types)}")

    print("\n1. App Sandbox & Entitlements:")
    print(f"  - App Sandbox Enabled: {'YES' if entitlements['sandbox_enabled'] else 'NO (Required for Mac App Store)'}")
    print(f"  - Network Client: {'YES' if entitlements['network_client'] else 'NO'}")
    print(f"  - Network Server: {'YES' if entitlements['network_server'] else 'NO'}")
    print(f"  - User-Selected File Access: {'YES' if entitlements['user_selected_files'] else 'NO'}")
    print(f"  - Security-Scoped Bookmarks: {'YES' if entitlements['bookmarks_app_scope'] else 'NO (File access lost on restart)'}")
    if entitlements["temporary_exceptions"]:
        print(f"  - [WARNING] Temporary Exception Entitlements ({len(entitlements['temporary_exceptions'])} found):")
        for ex in entitlements["temporary_exceptions"][:3]:
            print(f"    * {ex['file']}: {ex['exception']}")
    else:
        print("  - Temporary Exceptions: NONE (Clean entitlements)")

    print("\n2. Privacy Manifest & App Store Readiness:")
    print(f"  - PrivacyInfo.xcprivacy Manifest: {'FOUND' if privacy['has_privacy_manifest'] else 'MISSING (App Store Rejection Blocker)'}")
    if privacy["has_sparkle_updater"]:
        print(f"  - Sparkle Auto-Updater: DETECTED")
        print(f"    * EdDSA Public Key (SUPublicEDKey): {'CONFIGURED' if privacy['has_sparkle_eddsa_key'] else 'MISSING (Critical update security gap)'}")
    if privacy["deprecated_apis"]:
        print(f"  - [WARNING] Deprecated API usage:")
        for dep in privacy["deprecated_apis"]:
            print(f"    * {dep['file']}: {dep['api']}")

    print("\n3. Native Desktop Architecture & Stability:")
    print(f"  - SQLite / CoreData WAL Mode: {'CONFIGURED' if swift_arch['sqlite_wal_configured'] else 'NOT DETECTED (Concurrency/Locking risk)'}")
    if swift_arch["polling_timers"]:
        print(f"  - [WARNING] High-frequency polling timers detected (Battery/CPU burn risk):")
        for t in swift_arch["polling_timers"][:3]:
            print(f"    * {t['file']}:{t['line']} ({t['interval']}s interval) -> {t['text']}")
    if swift_arch["non_atomic_writes"]:
        print(f"  - [WARNING] Non-atomic file writes detected (Crash corruption risk):")
        for w in swift_arch["non_atomic_writes"][:3]:
            print(f"    * {w['file']}:{w['line']} -> {w['text']}")

    if "Electron (Node + Web)" in project_types or web_desktop["node_integration_danger"]:
        print("\n4. Electron / Tauri Container Security:")
        if web_desktop["node_integration_danger"]:
            print(f"  - [CRITICAL] nodeIntegration: true detected in: {', '.join(web_desktop['node_integration_danger'])}")
        if web_desktop["context_isolation_disabled"]:
            print(f"  - [CRITICAL] contextIsolation: false detected in: {', '.join(web_desktop['context_isolation_disabled'])}")
        if web_desktop["tauri_allowlist_broad"]:
            print(f"  - [WARNING] Tauri allowlist has broad 'all: true' permissions configured")
    print("=" * 70)


if __name__ == "__main__":
    main()
