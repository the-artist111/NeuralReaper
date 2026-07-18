# NeuralReaper Architecture

## Overview

NeuralReaper is an MCP (Model Context Protocol) server that bridges Claude AI with a sandboxed offensive security toolchain. Every tool runs inside a locked-down, non-root Docker container over stdio — there is no persistent network listener, no exposed port, and no state retained between sessions beyond Docker's own layer caching.

## Execution Model

```
┌─────────────────────────────────────────────────────────┐
│ Claude Desktop (Windows / macOS / Linux)                 │
│                                                          │
│  [User types natural language in chat]                   │
│           ↓                                               │
│  [Claude interprets as tool call]                        │
│           ↓                                               │
│  [MCP protocol → stdio to Docker container]              │
└─────────────────────────────────────────────────────────┘
           ↓ (stdio, not network)
┌─────────────────────────────────────────────────────────┐
│ Docker Container (neuralreaper:latest)                   │
│                                                          │
│  [FastMCP server starts]                                 │
│           ↓                                               │
│  [Receives tool call as JSON-RPC]                        │
│           ↓                                               │
│  [Dispatches to appropriate tool wrapper]                │
│           ↓                                               │
│  [Tool runs under 'pentester' user, scoped caps]         │
│           ↓                                               │
│  [Output → JSON response back over stdio]                │
│           ↓                                               │
│  [Container exits; --rm flag cleans it up]               │
└─────────────────────────────────────────────────────────┘
           ↓ (stdout/stderr)
┌─────────────────────────────────────────────────────────┐
│ Claude Desktop (continues conversation)                  │
└─────────────────────────────────────────────────────────┘
```

## Security Design

### Non-Root Execution
- Container runs as unprivileged `pentester` user
- Only nmap and masscan receive elevated capabilities via `setcap`
- No `--privileged` flag; no wholesale capability grant

### Input Sanitization
- Every target parameter validated against allow-list regex before subprocess dispatch
- No shell invocation; arguments passed as list, not string concatenation
- Command injection surface eliminated

### Timeout Enforcement
- Every tool call bounded by `MAX_TOOL_RUNTIME` (default 180s)
- Hung scans cannot hang the MCP session indefinitely
- Subprocess timeout exception caught and reported as `[TIMEOUT]` message

### Session Isolation
- Each tool call logged to in-memory `SESSION_LOG` via decorator
- Session log is **not** persistent across container lifetimes
- `generate_report()` compiles this session's data into one Markdown report
- On container exit, all logs are discarded; next session starts fresh

## Tool Module Organization

NeuralReaper is organized into 13 functional modules:

1. **Network Recon** (5 tools) — ping, traceroute, DNS, WHOIS, basic network validation
2. **Port Scanning** (4 tools) — nmap (quick, full, vuln scripts), masscan (ultra-fast)
3. **Web Scanning** (3 tools) — nikto, curl, openssl certificate inspection
4. **Content Discovery** (4 tools) — gobuster (dir + DNS), ffuf, dirb
5. **Nuclei CVE Engine** (5 tools) — scan, specific CVE, tech fingerprint, misconfig, custom tags + template update
6. **CVE Watchlist** (2 tools) — curated lookup-only orchestration against Nuclei + ExploitDB
7. **XSS & Injection** (2 tools) — xsstrike (WAF evasion), sqlmap
8. **CMS Scanning** (1 tool) — wpscan
9. **Active Directory & Identity** (4 tools) — Certipy (ADCS), BloodHound collection, bloodyAD enumeration, Impacket Kerberoast/AS-REProast
10. **Cryptographic Inventory & Post-Quantum** (3 tools) — TLS algo enum, SSH algo enum, HNDL risk classification
11. **Host Hardening & Rootkit Detection** (2 tools) — chkrootkit + rkhunter, Lynis audit
12. **Ransomware Exposure & Supply Chain** (2 tools) — external RDP/SMB/VPN check, OSV-Scanner dependency audit
13. **Fuzzing & Orchestration** (3 tools) — AFL++ harness, full_recon chains, session reporting

## Tool Wrapper Pattern

Every tool follows the same defensive pattern:

```python
@mcp.tool()
@log_session("tool_name")
def tool_name(target: str = "", extra: str = "") -> str:
    """One-line description of tool."""
    try:
        t = sanitize_target(target)        # Allow-list validation
        cmd = ["binary", "arg1"] + (...)   # List, never shell string
        return f"=== OUTPUT ===\n{run_command(cmd, timeout)}"
    except ValueError as e:
        return f"[INPUT ERROR] {e}"
```

This ensures:
- Input is validated before use
- Command is built as a list (no injection)
- Timeout is enforced
- Errors are caught and reported, not raised
- Output is always a string
- Tool call is logged to session

## Session Logging & Reporting

When a tool runs, the `@log_session` decorator intercepts the call:

```python
SESSION_LOG.append({
    "timestamp": "2026-06-28T17:45:32Z",
    "tool": "nmap_scan",
    "target": "192.168.1.1",
    "output": "<first 4000 chars of result>"
})
```

At any point, `generate_report()` can compile this into a single Markdown document with:
- Engagement start/end time
- All targets tested
- Severity summary (CRITICAL/HIGH/MEDIUM/LOW/INFO counts extracted from output)
- Complete tool-by-tool output log

This audit trail is **not** stored on disk by default — it exists only in memory for this session. `generate_report()` output is what you'd copy to disk for permanent record-keeping.

## Technology Stack

- **Runtime**: Python 3.11+ (native binary, no venv outside container)
- **MCP Framework**: FastMCP (Anthropic's lightweight MCP server helper)
- **Transport**: stdio (JSON-RPC 2.0)
- **Container**: Docker (Ubuntu 24.04 base)
- **Tooling**:
  - Network: nmap, masscan, whois, dig, traceroute, ping
  - Web: nikto, curl, openssl, ffuf, gobuster, dirb
  - Exploitation recon: sqlmap, xsstrike, wpscan, searchsploit
  - Vulnerability scanning: Nuclei (12,000+ templates, auto-updating)
  - Active Directory: Certipy, BloodHound.py, bloodyAD, Impacket suite
  - Cryptography: nmap NSE (ssl-enum-ciphers, ssh2-enum-algos)
  - Hardening: chkrootkit, rkhunter, Lynis
  - Fuzzing: AFL++
  - Supply chain: osv-scanner (Google)

## Limitations & Design Constraints

- **`--network host` on Docker Desktop**: Native Linux feature; on Windows/macOS Docker Desktop (which runs inside a managed VM), host-network-dependent scans may require bridge network + port mapping instead. Tracked as a known limitation.
- **No persistent state across sessions**: By design. Each container run is isolated; session logs are in-memory only.
- **No automated exploit payload generation**: Deliberate choice. Detection and enumeration only.
- **Authorized testing only**: Entire system is scoped for engagements where you own the target or have explicit written permission. Not intended for unauthorized scanning.

## Roadmap

- Native bridge-network mode for Windows/macOS Docker Desktop
- Structured JSON output mode per tool
- PDF export for `generate_report`
- CI pipeline auto-testing on every push
