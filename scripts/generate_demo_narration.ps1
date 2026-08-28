$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputDirectory = Join-Path $ProjectRoot "output\video"
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$Segments = @(
    "Ravi changed jobs, but his old provident fund account is unavailable to transfer. A visible name variation points him toward the wrong correction.",
    "As Ravi, I choose Find what blocks the transfer. ClaimSetu checks the fictional case and finds the real prerequisite: his previous employment has no Date of Exit.",
    "It also explains that the name variation is not causal here. I can inspect the rule, original value, and official EPFO source instead of trusting a black-box answer.",
    "I simulate the smallest correction. Only the fictional exit date changes; every check runs again, and the transfer prerequisite becomes met. No real EPFO record is touched.",
    "Now I get the official Manage, then Mark Exit route, its waiting condition, and when to retry. ClaimSetu turns a dead-end status into a safe next action.",
    "I built the decision core as versioned deterministic rules over evidence-preserving fictional records. Codex helped challenge the broad idea, verify sources, narrow the scope, and turn claims into tests.",
    "Reviewers can load a strict fictional JSON case and run the same check. The hosted build labels its browser fallback; the full container exposes identical rules through FastAPI.",
    "The correction is allowlisted and recomputed, not generated. Unknown fields and identifier-like names are rejected. There is no LLM in the decision path, so evidence stays repeatable.",
    "I chose no login and no real identifiers: no UAN, Aadhaar, PAN, OTP, or document upload. The journey works in Hindi, by keyboard, and at three hundred twenty pixels.",
    "That restraint is the design: explain one hidden prerequisite without pretending to be EPFO. ClaimSetu helps citizens correct the right thing before they try again."
)

for ($Index = 0; $Index -lt $Segments.Count; $Index++) {
    $OutputPath = Join-Path $OutputDirectory ("claimsetu-narration-{0:D2}.wav" -f ($Index + 1))
    $Escaped = [System.Security.SecurityElement]::Escape($Segments[$Index])
    $Ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-IN"><voice name="Microsoft Heera Desktop"><prosody rate="+35%">' + $Escaped + '</prosody></voice></speak>'
    $Synthesizer = [System.Speech.Synthesis.SpeechSynthesizer]::new()
    try {
        $Synthesizer.SetOutputToWaveFile($OutputPath)
        $Synthesizer.SpeakSsml($Ssml)
    }
    finally {
        $Synthesizer.Dispose()
    }
    Write-Output "NARRATION_SEGMENT=$OutputPath"
}
