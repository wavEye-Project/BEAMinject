"""
BEAMinjector module, made for BEAMinject

For usage as a module, check out the
"# Modify values for imported usage" section
of the code, and then configure accordingly
"""
__version__ = "0.4.7"

import os
import sys
import json
import secrets
import ctypes
import subprocess
import librosewater
import librosewater.module
import librosewater.process
import maxrm_mcpatch

# Modify values for imported usage
launchmc = True
def write_logs(*args, **kwargs):
    if sys.stdout:
        sys.stdout.write(*args, **kwargs)
        sys.stdout.flush()

def cleanquit(process_handle, arg):
    ctypes.windll.kernel32.CloseHandle(process_handle)
    return quitfunc(arg)
quitfunc = sys.exit
preview_version = False

# PROTECT THE UYGHURS
uyghurtext = secrets.choice([
    "Uyghur lives matter!",
    "Speak out for the Uyghurs!",
    "Demand justice for Uyghurs!",
    "Act now for Uyghur rights!",
    "Globalize Uyghur crisis!",
    "Fight Uyghur persecution!",
    "Unite for Uyghur rights!",
    "Solidarity with Uyghurs!",
    "Protect Uyghur culture!",
    "Judge Uyghur crisis response!",
    "Voice for silenced Uyghurs!",
    "Stop Uyghur genocide!"
])

# Identifier for inject_buildstr.py
buildstr = "custombuild"

def runcmd(args):
    try:
        return subprocess.check_output(args, stderr=subprocess.STDOUT, errors="ignore")
    except subprocess.CalledProcessError:
        pass

def main_():
    write_logs(f"* Hello from BEAMinjector, version {__version__}\n")
    write_logs(f"* Using Max-RM's patches, version {maxrm_mcpatch.__version__}\n")
    write_logs(f"* {uyghurtext}\n")

    if preview_version:
        package_name = "Microsoft.MinecraftWindowsBeta"
    else:
        package_name = "Microsoft.MinecraftUWP"
    payload = f'powershell.exe -c "Get-AppxPackage -name {package_name} | ' \
        'ForEach-Object { @($_.Version, $_.PackageFamilyName, ' \
        '(Join-Path $_.InstallLocation (Get-AppxPackageManifest $_).' \
        'Package.Applications.Application.Executable)) ' \
        '| ConvertTo-Json }"'
    write_logs(f"= Getting Minecraft{' Preview' if preview_version else ''} install... ")
    try:
        mcinstall = json.loads(runcmd(payload))
    except TypeError:
        write_logs("\n! Error while getting Minecraft install\n")
        return quitfunc(1)
    except json.JSONDecodeError:
        write_logs("\n! Minecraft not found\n")
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
        write_logs(f"\n! Couldn't wait for Minecraft (likely OS error)\n")
        return quitfunc(1)
    write_logs(f"found at PID {PID}!\n")

    # Get module address
    write_logs("= Waiting for module... ")
    try:
        module_address, _ = librosewater.module.wait_for_module(process_handle, "Windows.ApplicationModel.Store.dll")
    except librosewater.exceptions.ProcessClosedError:
        write_logs(f"\n! Minecraft process was closed\n")
        return cleanquit(process_handle, 1)
    write_logs(f"found at {hex(module_address)}!\n")

    # Dump module to variable
    write_logs("= Dumping module... ")
    try:
        data = librosewater.module.dump_module(process_handle, module_address)
    except librosewater.exceptions.ReadWriteError:
        write_logs(f"\n! Couldn't dump module, did Minecraft close?\n")
        return cleanquit(process_handle, 1)
    write_logs(f"done (read {len(data[1])} bytes)!\n")

    # Inject new module data
    write_logs("= Patching module... ")
    try:
        arch = maxrm_mcpatch.check_machine(mcinstall[2])
    except NotImplementedError:
        write_logs("\n! Couldn't find patches for platform, may be unsupported")
        return cleanquit(process_handle, 1)
    write_logs(f"got architecture {arch}... ")

    # The reason why we don't check error here is because
    # it's guaranteed to be one of the supported architectures
    # by the patches. The check is there for external usage of
    # the Max-RM hex patches.
    new_data = maxrm_mcpatch.patch_module(arch, data[1])
    write_logs("done!\n")

    write_logs("= Injecting module... ")
    try:
        librosewater.module.inject_module(process_handle, module_address, new_data)
    except librosewater.exceptions.ReadWriteError:
        write_logs(f"\n! Couldn't inject module, did Minecraft close?\n")
        cleanquit(process_handle, 1)
    write_logs(f"done (wrote {len(new_data)} bytes)!\n")

    write_logs("* Patched successfully!\n")
    cleanquit(process_handle, 0)

def main():
    try:
        main_()
    except Exception as ex:
        write_logs(f"\n! Uncaught error of type {type(ex).__name__} \
occured: {str(ex)}")
        return quitfunc(1)

if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview_version = True
    main()
