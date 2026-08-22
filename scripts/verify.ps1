$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location (Join-Path $ProjectRoot "apps/api")
try {
    python -m ruff check app tests
    if ($LASTEXITCODE -ne 0) { throw "Ruff failed" }
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw "Backend tests failed" }
    python -m compileall -q app tests
    if ($LASTEXITCODE -ne 0) { throw "Python compile check failed" }
}
finally {
    Pop-Location
}

Push-Location (Join-Path $ProjectRoot "apps/web")
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw "npm ci failed" }
    npm audit --audit-level=high
    if ($LASTEXITCODE -ne 0) { throw "npm audit failed" }
    npm test
    if ($LASTEXITCODE -ne 0) { throw "Frontend tests failed" }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
    npm run e2e
    if ($LASTEXITCODE -ne 0) { throw "Browser tests failed" }
}
finally {
    Pop-Location
}

Write-Output "Handover29C verification passed"
