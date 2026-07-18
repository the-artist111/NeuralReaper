# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [3.0.0] — 2026-06-28

### Added
- **Active Directory & Identity module**: `certipy_find` (ADCS ESC1–16 misconfig enumeration), `bloodhound_collect` (data collection for offline BloodHound GUI analysis), `bloodyad_enum` (ACL/object enumeration over LDAP), `kerberoast_check` / `asreproast_check` (Impacket-based weak-Kerberos-config detection)
- **Cryptographic Inventory / Post-Quantum module**: `crypto_inventory` and `ssh_crypto_check` (TLS/SSH algorithm enumeration via nmap NSE scripts), `pqc_readiness_check` (Harvest-Now-Decrypt-Later risk classification — flags RSA/ECC-only key exchange vs. PQ-hybrid groups)
- **Recent CVE Watchlist**: `cve_watchlist_scan` / `cve_watchlist_show` — lookup-only orchestration of Nuclei + ExploitDB against a curated, independently-verified list of recent high-severity CVEs (libssh2 CVE-2026-55200, Splunk CVE-2026-20253, Netlogon CVE-2026-41089, AD DS CVE-2026-25177, FFmpeg CVE-2026-8461). Writes zero new detection or exploit logic — purely calls existing templates/entries.
- **Host Hardening & Rootkit Detection**: `rootkit_check` (chkrootkit + rkhunter) and `host_hardening_audit` (Lynis) — established OSS signature-based tools, with explicit documentation that they audit whatever host they execute on
- **Ransomware-Relevant Exposure Check**: `ransomware_exposure_check` — external attack-surface check for the services most commonly abused as ransomware initial-access vectors (RDP/SMB/VPN), explicitly framed as exposure analysis, not infection detection
- **Supply Chain module**: `dependency_audit` wrapping Google's OSV-Scanner against a mounted project directory
- **Fuzzing module**: `fuzz_binary` — AFL++ harness automation against a locally-supplied instrumented binary
- **OWASP Reference Checklists**: `owasp_web_top10` and `owasp_agentic_top10` — static informational mappings of NeuralReaper's tool coverage against both frameworks
- **`full_recon` orchestrator** — chains DNS/WHOIS/port/tech-fingerprint recon into a single attack-surface summary with suggested test priorities based on detected technology stack
- **Session reporting**: `generate_report` and `clear_session_log` — every tool call this session is logged in-memory (via a `log_session` decorator) and can be compiled into one Markdown report with a severity summary on demand
- A **Design Philosophy** section in the README documenting the deliberate decision not to include automated exploit-payload generation, with the HexStrike-AI/Citrix NetScaler weaponization incident as the documented rationale

### Changed
- Dockerfile now installs `gdb`, `chkrootkit`, `rkhunter`, `lynis`, `afl++` (all confirmed-available Ubuntu 24.04 apt packages) and `osv-scanner` (via the existing Go toolchain)
- `requirements.txt` now includes `impacket`, `certipy-ad`, `bloodhound`, `bloodyAD`

### Notes
- All eight CVE IDs referenced in this release's design discussion were independently verified against public reporting before being referenced or added to `CVE_WATCHLIST` — none are taken on faith from secondary AI-generated summaries
- PingCastle was deliberately **not** integrated — it's a .NET/Windows-only tool meant to run on a domain-joined host, not from a Linux container; forcing it via Wine/Mono would be fragile and is not worth the reliability cost

## [2.0.0] — 2026-06-23

### Added
- **Nuclei** auto-CVE engine — six dedicated tools (`nuclei_scan`,
  `nuclei_cve`, `nuclei_tech`, `nuclei_misconfig`, `nuclei_wordlist_scan`,
  `nuclei_update`) backed by 12,000+ community-maintained templates
- **XSStrike** for XSS detection with WAF fingerprinting
- **masscan** for full 65535-port high-speed sweeps
- **gobuster** (directory + DNS modes) and **ffuf** for faster content
  discovery alongside the original `dirb`
- `nmap_vuln` — dedicated nmap `--script=vuln` wrapper
- `tests/smoke_test.sh` for build verification
- `docker-compose.yml` as an alternative to manual `docker run` invocations
- `SECURITY.md`, `CONTRIBUTING.md`, this changelog

### Changed
- **Base image migrated from `kalilinux/kali-rolling` to `ubuntu:24.04`**
  after the Kali rolling mirror hit a broken `gcc-16`/`libexpat1`
  dependency chain that made `apt-get install` fail consistently
- `wpscan` now installed via `gem install` (not Ubuntu-packaged)
- `ffuf` now installed from a pinned GitHub release binary (not
  Ubuntu-packaged)
- `searchsploit` now installed via a direct clone of the official
  ExploitDB GitLab repository

### Fixed
- Docker build failures caused by Kali's broken rolling-repo dependency
  resolution
- MCP server showing `failed` / `Server disconnected` in Claude Desktop —
  root cause was Docker Desktop not running yet when Claude Desktop
  attempted to spawn the container (`npipe:////./pipe/dockerDesktopLinuxEngine`
  connection error)
- Tool list never appearing in Claude Desktop at all — root cause was a
  Microsoft Store install of Claude Desktop, which sandboxes the app and
  never reads `%APPDATA%\Claude\claude_desktop_config.json`

## [1.0.0] — 2026-05-27

### Added
- Initial release: FastMCP server wrapping `nmap`, `nikto`, `sqlmap`,
  `wpscan`, `dirb`, and `searchsploit`
- Non-root container execution with targeted `setcap` capabilities for
  `nmap`
- Input sanitization via allow-list regex on all target parameters
- `claude_desktop_config.json` for one-step Claude Desktop integration
