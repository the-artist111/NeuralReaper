# Full Recon Workflow Example

## Scenario: Authorized assessment of your lab environment (192.168.56.0/24)

### Phase 1: Quick Network Mapping

```
In Claude:
"Run a quick nmap on 192.168.56.10 to see what's open"
```

Claude calls `nmap_quick(target="192.168.56.10")` → returns top 1000 ports

### Phase 2: Full Recon with Orchestration

```
In Claude:
"Run full_recon on 192.168.56.10"
```

This chains:
1. DNS recon (if applicable)
2. WHOIS lookup
3. nmap quick scan
4. Technology fingerprinting via Nuclei
5. Automatically suggests test priorities based on detected stack

Output might be:
```
=== TECH FINGERPRINT ===
[tech-detect:nginx] nginx 1.24.0 detected
[tech-detect:php] PHP backend inferred

=== SUGGESTED TEST PRIORITIES ===
[nginx] detected -> prioritize testing: Misconfigured alias/path traversal, Request smuggling
[php] detected -> prioritize testing: LFI/RFI, Command Injection, Insecure Deserialization
```

### Phase 3: Deep Vulnerability Scanning

```
In Claude:
"Update Nuclei, then scan 192.168.56.10 for all critical and high severity issues"
```

Two calls:
1. `nuclei_update()` — pulls latest 12,000+ templates
2. `nuclei_scan(target="192.168.56.10", severity="critical,high")`

### Phase 4: Active Directory (if applicable)

```
In Claude:
"Check my lab domain for kerberoastable accounts and ADCS misconfigurations"
```

Chains:
1. `kerberoast_check()` — SPN-set users
2. `certipy_find()` — ESC1-16 template abuse paths

### Phase 5: Crypto Posture & Post-Quantum

```
In Claude:
"Check 192.168.56.10's TLS crypto for post-quantum readiness"
```

`pqc_readiness_check(target="192.168.56.10", port="443")` flags:
- RSA/ECC-only key exchange → HNDL exposed
- PQ-hybrid groups (X25519+ML-KEM) → safe
- Legacy protocols → should disable anyway

### Phase 6: Generate Report

```
In Claude:
"Generate a report of everything we found"
```

`generate_report()` outputs one Markdown with:
- Session start/end times
- Targets tested
- Severity breakdown (CRITICAL: 2, HIGH: 5, MEDIUM: 12)
- Complete tool-by-tool output log

Copy it to a file for your records.

---

## Key Takeaways

1. **Natural language in** — Claude interprets the intent
2. **Chained execution** — `full_recon` orchestrates 5+ tools at once
3. **Real output** — not a simulation; actual tool results
4. **Audit trail** — every call is logged and reportable
5. **Selective depth** — start broad with `full_recon`, then go deep on specific findings
