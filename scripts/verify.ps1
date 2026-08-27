$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location (Join-Path $ProjectRoot "apps/api")
try {
    python -m ruff check app tests_identity_rescue
    if ($LASTEXITCODE -ne 0) { throw "Ruff failed" }
    python -m pytest -q tests_identity_rescue
    if ($LASTEXITCODE -ne 0) { throw "Backend tests failed" }
    python -m compileall -q app tests_identity_rescue
    if ($LASTEXITCODE -ne 0) { throw "Python compile check failed" }
}
finally {
    Pop-Location
}

python (Join-Path $ProjectRoot "scripts/export_static_identity_rescue.py")
if ($LASTEXITCODE -ne 0) { throw "Static fixture export failed" }

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
    npm run build:pages
    if ($LASTEXITCODE -ne 0) { throw "Static Pages build failed" }
    npm run e2e:pages
    if ($LASTEXITCODE -ne 0) { throw "Static Pages browser tests failed" }
}
finally {
    Pop-Location
}

Write-Output "ClaimPath verification passed"
