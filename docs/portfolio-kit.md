# NeuralReaper — Portfolio Presentation Kit

Copy-paste ready content for GitHub, LinkedIn, and your resume.

---

## 1. GitHub Repository "About" Section

**Description (one-liner, fits GitHub's About field):**
```
AI-native security research platform — 46 MCP tools wiring Claude to real offensive security tooling (AD attack paths, post-quantum crypto assessment, auto-updating CVE engine, session reporting) via an isolated Docker container.
```

**Topics to add** (Settings gear next to "About" → Topics):
```
cybersecurity penetration-testing mcp model-context-protocol
docker active-directory post-quantum-cryptography bloodhound
certipy nuclei claude-ai python security-automation
ethical-hacking offensive-security fastmcp
```

---

## 2. LinkedIn Post Draft

```
Built NeuralReaper — an MCP server that gives Claude direct,
sandboxed execution access to a real offensive security toolchain,
not a wrapper around one API.

46 tools across network/web recon, an Active Directory attack-path
module (Certipy, BloodHound, bloodyAD, Impacket), a post-quantum
cryptography readiness checker that flags Harvest-Now-Decrypt-Later
exposure on live TLS handshakes, an auto-updating CVE engine backed
by Nuclei's 12,000+ community templates, and a session report
generator — all running in a locked-down, non-root Docker container.

The part actually worth reading is the engineering log in the repo's
CHANGELOG: a broken Kali rolling-repo dependency chain mid-build, a
WSL2/Docker Desktop integration gap, a Windows Store install that
silently sandboxed the config so the tool never even loaded. Every
fix is documented root-cause-first — that's the part that matters
more than the tool list.

One deliberate design choice: no automated exploit-payload
generation. A comparable framework shipped that and was reportedly
being weaponized against a Citrix zero-day within hours of release.
NeuralReaper stops at detection and enumeration on purpose.

Repo: [your GitHub link]

#cybersecurity #penetrationtesting #ai #activedirectory #mcp
```

---

## 3. Resume / CV Bullet Points

**Under a "Personal Projects" or "Technical Projects" section:**

```
NeuralReaper — AI-Integrated Security Research Platform
- Designed and built a 46-tool MCP (Model Context Protocol) server
  integrating Claude with a containerized offensive security
  toolchain (Nmap, Nuclei, Certipy, BloodHound, sqlmap, AFL++),
  enabling natural-language-driven reconnaissance, Active Directory
  attack-path enumeration, and post-quantum cryptographic risk
  assessment
- Implemented least-privilege execution design: non-root container,
  scoped Linux capabilities (CAP_NET_RAW/CAP_NET_ADMIN via setcap),
  and allow-list input sanitization to eliminate shell-injection
  surface across all tool wrappers
- Diagnosed and resolved cross-platform integration failures across
  Docker Desktop, WSL2, and a sandboxed application install,
  documenting root-cause analysis for each in a public changelog
- Built a session-logging and automated report-generation system
  that compiles multi-tool engagement output into a single
  Markdown report with severity classification
```

---

## 4. Short Bio Blurb (for a portfolio site or cover letter)

```
I build security tooling that treats "AI-assisted" as a discipline,
not a gimmick. NeuralReaper is a Model Context Protocol server that
gives Claude direct execution access to a real offensive security
toolchain — network/web recon, Active Directory attack-path mapping,
post-quantum cryptographic risk assessment, and an auto-updating
CVE engine — running isolated in a non-root Docker container, with
no automated exploit generation by design. I care as much about the
documented debugging trail as the feature list, because that's what
actually shows how a system was built, not just what it does.
```

---

## Notes

- Swap `[your GitHub link]` for your actual repo URL before posting.
- Keep resume bullets to whichever 2-3 are most relevant to the role
  you're applying for — don't dump all 4 on every application.
- If a recruiter asks about the "no exploit generation" design choice
  in an interview, that's a great opening to talk about HexStrike AI's
  weaponization incident — it shows you think about misuse, not just
  features.
