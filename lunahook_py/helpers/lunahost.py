from ctypes import *
from ctypes.wintypes import DWORD, LPCWSTR
from .arch import detect_arch, Arch
from .lunasubprocess import inject as inject_subprocess

class ThreadParam(Structure):
    _fields_ = [
        ("processId", c_uint),
        ("addr",      c_uint64),
        ("ctx",       c_uint64),
        ("ctx2",      c_uint64),
    ]

ProcessEvent        = CFUNCTYPE(None, DWORD)
ThreadEvent         = CFUNCTYPE(None, c_wchar_p, c_char_p, ThreadParam)
ThreadEventEmbed    = CFUNCTYPE(None, c_wchar_p, c_char_p, ThreadParam, c_bool)
OutputCallback      = CFUNCTYPE(None, c_wchar_p, c_char_p, ThreadParam, c_wchar_p)
HostInfoHandler     = CFUNCTYPE(None, c_int, c_wchar_p)
HookInsertHandler   = CFUNCTYPE(None, DWORD, c_uint64, c_wchar_p)
EmbedCallback       = CFUNCTYPE(None, c_wchar_p, ThreadParam)
I18NCallback        = CFUNCTYPE(c_void_p, c_wchar_p)
EmuGameInfoCallback = CFUNCTYPE(None, c_wchar_p, c_wchar_p, c_wchar_p)


class LunaHost:
    def __init__(self, path, on_output):
        # on_output: callable(hookcode, hookname, ThreadParam, text)
        self.host = CDLL(str(path / "LunaHost64.dll"))
        self.hook32 = path / "LunaHook32.dll"
        self.hook64 = path / "LunaHook64.dll"
        self.subp32 = path / "LunaSubprocess32.exe"
        self.subp64 = path / "LunaSubprocess64.exe"

        self.host.Luna_ConnectProcess.argtypes   = [DWORD]
        self.host.Luna_DetachProcess.argtypes    = [DWORD]
        self.host.Luna_CheckIfNeedInject.argtypes = [DWORD]
        self.host.Luna_CheckIfNeedInject.restype  = c_bool
        self.host.Luna_Start.argtypes = [
            ProcessEvent, ProcessEvent,
            ThreadEventEmbed, ThreadEvent,
            OutputCallback, HostInfoHandler,
            HookInsertHandler, EmbedCallback,
            I18NCallback, EmuGameInfoCallback,
        ]

        self._keepref = [
            ProcessEvent(lambda pid: None),
            ProcessEvent(lambda pid: None),
            ThreadEventEmbed(lambda hc, hn, tp, emb: None),
            ThreadEvent(lambda hc, hn, tp: None),
            OutputCallback(on_output),              # the one that matters
            HostInfoHandler(lambda t, msg: None),
            HookInsertHandler(lambda pid, addr, hc: None),
            EmbedCallback(lambda txt, tp: None),
            I18NCallback(lambda q: None),
            EmuGameInfoCallback(lambda a, b, c: None),
        ]
        self.host.Luna_Start(*self._keepref)

    def attach(self, pid: int):
        self.host.Luna_ConnectProcess(pid)

    def detach(self, pid: int):
        self.host.Luna_DetachProcess(pid)

    def injection_needed(self, pid: int) -> bool:
        return self.host.Luna_CheckIfNeedInject(pid)
        
    def inject(self, pid: int):
        p_arch = detect_arch(pid)
        exe, dll = (self.subp32, self.hook32) if p_arch == Arch.x86 else (self.subp64, self.hook64)
        inject_subprocess(exe_path=exe, dll_path=dll, pid=pid)