# Security Policy

NeuralReaper is an offensive security tool. This file covers security of the
**tool itself** — not the targets you point it at.

## Scope

NeuralReaper is intended for use against systems you own or have explicit
written authorization to test. It is not intended to be exposed to the
internet, run multi-tenant, or used as a hosted service. There is currently
no built-in authentication layer because the design assumption is a single
operator running the container locally via Claude Desktop over stdio.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | ✅ |
| 1.x     | ❌ |

## Reporting a Vulnerability

If you find a security issue in NeuralReaper itself — e.g. a command
injection path through an unsanitized parameter, a privilege escalation
inside the container, or a way to break out of the sandbox — please report
it privately rather than opening a public issue:

1. Open a [GitHub Security Advisory](../../security/advisories/new) on this
   repository, **or**
2. Email the maintainer directly (see GitHub profile) with the subject line
   `NeuralReaper Security Report`.

Please include:
- A clear description of the issue and its impact
- Steps to reproduce
- Affected version / commit hash

You can expect an initial response within 72 hours. Please give a reasonable
window to fix the issue before any public disclosure.

## Design Notes Relevant to Security Review

- All container processes run as a non-root user (`pentester`).
- Only `nmap` and `masscan` carry elevated capabilities (`CAP_NET_RAW`,
  `CAP_NET_ADMIN`), granted via `setcap` rather than running the container
  `--privileged`.
- All target inputs are validated against an allow-list regex before being
  passed to `subprocess.run()` as an argument list (never through a shell),
  which removes the classic shell-injection vector.
- Every tool invocation has an enforced timeout to prevent resource
  exhaustion via a hung scan.
