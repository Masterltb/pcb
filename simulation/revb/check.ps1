param([switch]$SkipBuild)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$projectPath = $PSScriptRoot
if (-not $SkipBuild) {
    & pio run --project-dir $projectPath
    if ($LASTEXITCODE -ne 0) { throw 'ESP32 build failed' }
}
& python -m unittest discover -s (Join-Path $projectPath 'tests') -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Server/diagram checks failed' }
$compiler = Get-Command g++ -ErrorAction SilentlyContinue
if ($compiler) { $compilerPath = $compiler.Source }
else {
    $compilerPath = Join-Path $env:USERPROFILE '.platformio\packages\toolchain-gccmingw32\bin\g++.exe'
    if (-not (Test-Path -LiteralPath $compilerPath)) {
        throw 'Install g++, or run: pio pkg install --global --tool platformio/toolchain-gccmingw32'
    }
    $env:PATH = (Split-Path $compilerPath) + ';' + $env:PATH
}
$executablePath = Join-Path $projectPath 'test-controller.exe'
& $compilerPath -std=c++11 -Wall -Wextra -Werror (Join-Path $projectPath 'tests/controller_test.cpp') -o $executablePath
if ($LASTEXITCODE -ne 0) { throw 'Controller test compile failed' }
& $executablePath
if ($LASTEXITCODE -ne 0) { throw 'Controller scenarios failed' }
