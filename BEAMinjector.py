"""
BEAMinjector module, made for BEAMinject

For usage as a module, check out the
"# Modify values for imported usage" section
of the code, and then configure accordingly
"""
__version__ = "0.4.1"

import os
import sys
import json
import ctypes
import subprocess
import librosewater
import librosewater.module
import librosewater.process
import maxrm_mcpatch

# Modify values for imported usage
launchmc = True
if sys.stdout:
    def write_logs(*args, **kwargs):
        sys.stdout.write(*args, **kwargs)
        sys.stdout.flush()
else:
    # sys.stdout doesn't exist, so we can just write a dummy function
    def write_logs(*args, **kwargs):
        pass

def cleanquit(process_handle, quit_func, arg):
    ctypes.windll.kernel32.CloseHandle(process_handle)
    return quit_func(arg)
quitfunc = sys.exit

# Identifier for inject_buildstr.py
buildstr = "custombuild"

def getres(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def runcmd(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT)

def main_():
    write_logs(f"* Hello from BEAMinjector, version {__version__}\n")
    write_logs(f"* Using Max-RM's patches, version {maxrm_mcpatch.__version__}\n")
    write_logs("= Getting Minecraft install... ")
    try:
        mcinstall = runcmd(f'powershell.exe -ExecutionPolicy Bypass -File "{getres("getmc.ps1")}"')
    except subprocess.CalledProcessError as ex:
        write_logs("\n! Call to system failed\n")
        write_logs("! {ex}\n")
        return quitfunc(1)
    try:
        mcinstall = json.loads(mcinstall)
    except TypeError:
        write_logs("\n! Couldn't find Minecraft\n")
        return quitfunc(1)
    write_logs(f"found version {mcinstall[0]}!\n")

    # Wait for Minecraft
    if launchmc:
        write_logs("* Launching Minecraft\n")
        runcmd(f'powershell.exe explorer.exe shell:AppsFolder\\{mcinstall[1]}!App')
    write_logs("= Waiting for Minecraft to launch... ")
    mcapp = os.path.basename(mcinstall[2])
    try:
        PID, process_handle = librosewater.process.wait_for_process(mcapp)
    except librosewater.exceptions.QueryError:
        write_logs(f"! Couldn't wait for Minecraft (likely OS error)\n")
        return quitfunc(1)
    write_logs(f"found at PID {PID}!\n")

    # Get module address
    write_logs("= Waiting for module... ")
    try:
        module_address, _ = librosewater.module.wait_for_module(process_handle, "Windows.ApplicationModel.Store.dll")
    except librosewater.exceptions.QueryError:
        write_logs(f"\n! Couldn't wait for module, did Minecraft close?\n")
        return cleanquit(process_handle, quitfunc, 1)
    write_logs(f"found at {hex(module_address)}!\n")

    # Dump module to variable
    write_logs("= Dumping module... ")
    try:
        data = librosewater.module.dump_module(process_handle, module_address)
    except librosewater.exceptions.ReadWriteError:
        write_logs(f"\n! Couldn't dump module, did Minecraft close?\n")
        return cleanquit(process_handle, quitfunc, 1)
    write_logs(f"done (read {len(data[1])} bytes)!\n")

    # Inject new module data
    write_logs("= Patching module... ")
    try:
        arch = maxrm_mcpatch.check_machine(mcinstall[2])
    except NotImplementedError:
        write_logs("\n! Couldn't find patches for platform, may be unsupported")
        return cleanquit(process_handle, quitfunc, 1)
    write_logs(f"got architecture {arch}... ")
    new_data = maxrm_mcpatch.patch_module(arch, data[1])
    write_logs("done!\n")

    write_logs("= Injecting module... ")
    try:
        librosewater.module.inject_module(process_handle, module_address, new_data)
    except librosewater.exceptions.ReadWriteError:
        write_logs(f"\n! Couldn't inject module, did Minecraft close?\n")
        cleanquit(process_handle, quitfunc, 1)
    write_logs(f"done (wrote {len(new_data)} bytes)!\n")

    write_logs("* Patched successfully!\n")
    cleanquit(process_handle, quitfunc, 0)

def main():
    try:
        main_()
    except Exception as ex:
        write_logs(f"\n! Uncaught error of type {type(ex).__name__} \
occured: {getattr(ex, 'message', str(ex))}")
        return quitfunc(1)

if __name__ == "__main__":
    main()
