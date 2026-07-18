# Contributing to NeuralReaper

Pull requests adding new tool wrappers are welcome. Because tools are loaded
into Claude Desktop through an MCP gateway that is stricter than plain
Python, there are a handful of non-obvious constraints every tool function
must follow — violating them doesn't raise a Python error, it silently
breaks the gateway at runtime, which is much harder to debug. Please read
this in full before opening a PR.

## Hard Constraints for Tool Functions

1. **No `@mcp.prompt()` decorators.** They break Claude Desktop's gateway.
2. **No `prompt` parameter passed to `FastMCP()`.** Same issue.
3. **No `typing` module type hints.** No `Optional`, `Union`, `List[str]`,
   etc. Stick to plain `str`, `int`, `bool`.
4. **No complex default values.** Use `param: str = ""`, never
   `param: str = None`.
5. **Single-line docstrings only.** Multi-line docstrings on a `@mcp.tool()`
   function have been observed to cause gateway panic errors. Keep it to one
   line describing what the tool does.
6. **Every tool must return a `str`.** Format whatever the underlying
   command produces into a string — don't return dicts, lists, or `None`.
7. **Every tool must handle its own errors.** Catch exceptions inside the
   function and return a readable `[ERROR] ...` string rather than letting
   an exception propagate.

## Adding a New Tool Wrapper

A minimal wrapper looks like this:

```python
@mcp.tool()
def mytool_scan(target: str = "", extra_flags: str = "") -> str:
    """One-line description of what mytool_scan does."""
    try:
        t = sanitize_target(target)
        cmd = ["mytool", "-target", t] + (shlex.split(extra_flags) if extra_flags else [])
        return f"=== MYTOOL: {t} ===\n{run_command(cmd, 120)}"
    except ValueError as e:
        return f"[INPUT ERROR] {e}"
```

Checklist before opening a PR:

- [ ] Target/input is passed through `sanitize_target()` (or an equivalent
      allow-list check) before being used in a command
- [ ] The command is built as a **list** of arguments, never a shell string
- [ ] A reasonable timeout is passed to `run_command()`
- [ ] The function has exactly one line in its docstring
- [ ] The new binary is added to the `Dockerfile` with a confirmed install
      method (test the `apt-get`/`gem`/binary-download path before submitting)
- [ ] `tool_help()`'s output string is updated to list the new tool
- [ ] You've run `tests/smoke_test.sh` against your rebuilt image

## Testing Locally

```bash
docker build -t neuralreaper:latest .
bash tests/smoke_test.sh
```

If the smoke test passes, do a manual check with the full `tools/list`
handshake to confirm your new tool shows up:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}\n' | \
  docker run --rm -i --network host --cap-add NET_RAW --cap-add NET_ADMIN neuralreaper:latest
```

## Pull Request Process

1. Fork the repo and create a branch off `main`
2. Make your change, following the checklist above
3. Open a PR describing the tool added and why it's useful
4. Be responsive to review — most feedback will be about the constraints
   above, since they're easy to violate by accident
