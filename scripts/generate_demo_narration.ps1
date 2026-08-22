$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputDirectory = Join-Path $ProjectRoot "output\video"
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$Segments = @(
    "Public service portals often say details do not match, but not which record actually blocks the task. Identity Rescue uses fictional data to answer that one question.",
    "Ananya cannot fetch a Driving Licence. In one click we see the two original name forms and the causal, versioned demo rule, without entering any real ID.",
    "The evidence separates official source support from the exact prototype predicate. The planner compares only allowed corrections and prefers the lower impact issuer route over changing a broadly reused upstream record.",
    "Simulation changes only this fictional case. The engine recomputes readiness, shows before and after, and says clearly that no official record was changed.",
    "The journey ends with a linked official source and a warning to verify the current process before acting.",
    "The key innovation is causal disambiguation. Arvind's names look different, but changing the name does not fix the case. The service history condition is the modeled blocker.",
    "For a life event, the minimum plan updates only the Driving Licence name needed for the selected goal. PAN and address differences remain visible instead of being changed for cosmetic consistency.",
    "The same focused flow works in simple Hindi, at three hundred and twenty pixels, with keyboard navigation, visible focus, live status announcements, and no horizontal scroll.",
    "Codex helped turn the frozen specifications into deterministic rules, planner tests, a React and FastAPI implementation, accessibility gates, Docker verification, and public deployment. AI is not allowed to decide readiness or the plan.",
    "It is an independent prototype: fictional data, no government connection, and no claim beyond the evidence."
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
