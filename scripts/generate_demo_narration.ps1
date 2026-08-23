$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputDirectory = Join-Path $ProjectRoot "output\video"
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$Segments = @(
    "A blocked provident fund claim can show several record differences, but never explain which one actually matters. ClaimPath turns that confusion into one focused pre-flight.",
    "Ravi's fictional withdrawal involves forty five thousand rupees. The citizen can describe what happened, but the note stays only in this browser and cannot change the diagnosis.",
    "ClaimPath compares the original Aadhaar-linked, PAN, EPFO, and employment-history facts. Versioned rules preserve provenance instead of producing an unexplained identity score.",
    "The visible Ravi K and Ravi Kumar forms are compatible through an explicit fictional relation. The causal blocker is the missing Date of Exit, not the name.",
    "The technical drawer exposes the rule version, original value, evidence status, source, uncertainty, and the boundary between official guidance and prototype logic.",
    "A minimum-cost planner searches only allowlisted actions. It changes the fictional Date of Exit, recomputes every check, and leaves the non-causal name variation untouched.",
    "The architecture is deliberately deterministic: evidence model, causal rules, planner, counterfactual simulation, then official handoff. AI cannot decide readiness or select a correction.",
    "Privacy comes from not collecting. There is no real UAN, Aadhaar, PAN, OTP, payment, biometric, upload, government API call, or official write.",
    "The interface uses one primary action per state, visible progress, strong contrast, responsive evidence panels, keyboard semantics, and a complete English and Hindi journey.",
    "Modeled checks are not approval. The EPFO Member Portal and UMANG provide two official exits."
)

for ($Index = 0; $Index -lt $Segments.Count; $Index++) {
    $OutputPath = Join-Path $OutputDirectory ("identity-rescue-narration-{0:D2}.wav" -f ($Index + 1))
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
