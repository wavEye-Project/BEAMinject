$mcpack = Get-AppxPackage -name Microsoft.MinecraftUWP
if ($mcpack) {
    $mcmans = $mcpack | Get-AppxPackageManifest
    if ($mcmans) {
        $mcpath = Join-Path $mcpack.InstallLocation $mcmans.Package.Applications.Application.Executable
        (@($mcpack.Version, $mcpack.PackageFamilyName, $mcpath) | ConvertTo-Json)
    }
}