# lunahook-py

Python wrapper for [LunaHook](https://github.com/HIllya51/LunaTranslator) — attach to running Windows VN/game processes, inject text hooks, and stream extracted text into your own tools. Zero runtime dependencies.

---

## What is this?

LunaHook is the text hooking engine behind [LunaTranslator](https://github.com/HIllya51/LunaTranslator), a successor to the previously popular Textractor. It supports a much wider range of games than the older Textractor, with monthly updates for new titles.

`lunahook-py` wraps LunaHook's DLLs in a clean Python API so you can plug text hooking into your own projects — translation pipelines, subtitle overlays, logging tools, whatever you're building.

The LunaHook binaries are bundled with the package. You don't need a separate LunaTranslator installation.

---

## Requirements

- Python 3.10+
- Windows 10/11 (x64)
- [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) (already installed on most machines)
- Admin privileges (required for DLL injection)

---

## Installation

```bash
pip install lunahook-py
```

---

## Quick Start

```python
from lunahook_py import LunaHook

lh = LunaHook()
lh.attach(12345)  # your game's PID

for pid, hook, text in lh.listen():
    print(text)
```

---

## Usage

### Filtering by hook

When you attach to a game, LunaHook will discover multiple text threads — story text, UI strings, system calls, noise. Each one has a hook code like `ENHQX-24@10DD90:game.exe`. Once you know which hook carries the story text, filter to it:

```python
for pid, hook, text in lh.listen(pid=12345, hook="ENHQX-24@10DD90:game.exe"): #Both parameters are optional
    print(text)
```

To discover which hooks are available, listen without a filter first and watch what comes through.

### Listening to everything

```python
# No filters — see all output from all attached processes
for pid, hook, text in lh.listen():
    print(f"[{pid}] {hook}: {text}")
```

### Attaching multiple games

```python
lh.attach(111)
lh.attach(222)  # spins up a second LunaHost instance if architectures differ

for pid, hook, text in lh.listen(): #Here you could use the pid parameter for filtering too
    print(f"[{pid}] {text}")
```

### Detaching

```python
lh.detach(12345)
```

---

## API

### `LunaHook()`

Creates a new LunaHook instance and initializes the host DLL.

### `.attach(pid: int)`

Attaches to a running process. Automatically detects x86/x64 architecture and injects the appropriate hook DLL. If the process is already hooked (e.g. from a previous session), injection is skipped.

### `.detach(pid: int)`

Detaches from a process.

### `.listen(pid: int = 0, hook: str = None)`

Blocking generator that yields `(pid, hook, text)` tuples as text arrives.

| Parameter | Description |
|-----------|-------------|
| `pid` | Filter to a specific process. `0` means all attached processes. |
| `hook` | Filter to a specific hook code string. `None` means all hooks. |

---

## Notes

**Admin privileges** — DLL injection requires elevated permissions. Run your script as administrator, or you'll get silent injection failures.

**x86 games** — 32-bit games are fully supported. `lunahook-py` detects the target architecture automatically and uses the right injector.

**Hook discovery** — LunaHook auto-discovers text threads when you attach. Give it a second after attaching and advance some text in the game before listening — this lets the hooks fire and populate the output stream.

**Compared to textractor-py** — `lunahook-py` uses the same `listen()` interface as [`textractor-py`](https://github.com/arima57/textractor-py), so they're largely drop-in compatible from the caller's perspective. LunaHook supports more games and gets more frequent updates; Textractor is simpler but increasingly unmaintained.

---

## License

GPLv3.0 — matching LunaHook's upstream license.
