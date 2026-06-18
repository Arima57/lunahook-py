from lunahook_py import LunaHook

lh = LunaHook()
print("attempting injection")
lh.attach(6836)
print("attached, please wait")

for pid, hook, text in lh.listen():
    print(f"[{pid}] {hook}: {text}")