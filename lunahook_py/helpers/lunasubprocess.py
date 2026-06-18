from subprocess import run
def inject(exe_path, dll_path, pid:int) -> int:
    resp = run(f'"{exe_path}" dllinject {pid} "{dll_path}"', shell=True)    
    return resp.returncode