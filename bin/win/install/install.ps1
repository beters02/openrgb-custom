$ScoopBuckets = @(
    "main"
    "extras"
)

$Dependencies = @(
    @{
        Name    = "Python"
        Winget  = "Python.Python.3.13"
        Scoop   = "main/python@3.13"
        Check   = { python3 --version }
    },
    @{
        Name    = "OpenRGB"
        Winget  = "OpenRGB.OpenRGB"
        Scoop   = "extras/openrgb"
        Check   = { Test-Path -Path "C:\Program Files\OpenRGB\OpenRGB.exe" }
    },
    @{
        Name    = "Go"
        Winget  = "GoLang.Go"
        Scoop   = "main/go"
        ScoopBucket = "lune https://github.com/CompeyDev/lune-packaging.git"
        Check   = { go --version }
    }
)

function Update-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Test-Admin {
    # --- Self-elevate if not running as admin ---
    if (-not ([Security.Principal.WindowsPrincipal] `
        [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {

        Write-Host "Requesting administrator privileges..."

        $run_args = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        Start-Process powershell -Verb RunAs -ArgumentList $run_args
        exit
    }
}

function Assert-Has-Chocolatey {
    Get-Command choco -ErrorAction SilentlyContinue | Out-Null
    return $?
}

function Install-Chocolatey {
    Write-Host "Installing Chocolatey..."

    Set-ExecutionPolicy Bypass -Scope Process -Force

    [System.Net.ServicePointManager]::SecurityProtocol = `
        [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

    Invoke-Expression (
        (New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1")
    )

    Update-Path
}

function Assert-Has-WinGet {
    Get-Command winget -ErrorAction SilentlyContinue | Out-Null
    return $?
}
function Install-WinGet {
    $wingetUri = "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    $temp = "$env:TEMP\winget.msixbundle"

    Invoke-WebRequest -Uri $wingetUri -OutFile $temp

    Add-AppxPackage -Path $temp

    Update-Path
}

function Assert-Has-Scoop {
    Get-Command scoop -ErrorAction SilentlyContinue | Out-Null
    return $?
}

function Install-Scoop {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
    Update-Path
}

function Install-Scoop-Bucket {
    
}

function Assert-Dependency-Installed {
    param ($Dep)

    if (-not $Dep.Check) { return $false }

    try {
        & $Dep.Check | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Install-Dependency {
    param (
        [Parameter(Mandatory)]
        [hashtable]$Dep,

        [Parameter(Mandatory)]
        [ValidateSet("winget","scoop")]
        [string]$Installer
    )

    Write-Host "Installing $($Dep.Name)..."

    if ($Installer -eq "winget") {
        winget install --id $Dep.Winget `
            --silent `
            --accept-package-agreements `
            --accept-source-agreements
    }
    else {
        scoop install $Dep.Scoop
    }

    if ($Dep.Check) {
        try {
            & $Dep.Check | Out-Null
            Write-Host "✔ $($Dep.Name) installed"
        }
        catch {
            Write-Error "✖ $($Dep.Name) failed to install"
            exit 1
        }
    }
}

# START

# Verify user is admin
Test-Admin

# Install WinGet if necessary
if (-not (Assert-Has-Winget)) {
    Install-WinGet
}

# Decide package manager
if (Assert-Has-WinGet) {
    Write-Host "Installing Dependencies via WinGet"

    $PKG = "winget"
    #Install-Deps-WinGet
} else {
    Write-Warning "WinGet not found. Attempting Scoop Installation."

    if (-not (Assert-Has-Scoop)) {
        Install-Scoop
    }

    if (Assert-Has-Scoop) {
        Write-Host "Installing Dependencies via Scoop"

        # Install Scoop Buckets
        foreach ($buck in $ScoopBuckets) {
            Write-Host "Installing scoop bucket $($buck)"
            scoop bucket add $buck
        }

        $PKG = "scoop"
    } else {
        Write-Error "Scoop installation failed. Visit this link to install scoop and rerun this installer when finished.: https://github.com/ScoopInstaller/Scoop?tab=readme-ov-file#installation"
        exit 1
    }
}

# Install dependencies
foreach ($dep in $Dependencies) {
    if (Is-Installed $dep) {
        Write-Host "✔ $($dep.Name) already installed"
        continue
    }

    Install-Dependency -Dep $dep -Installer $PKG
}