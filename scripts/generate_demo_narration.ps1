$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputDirectory = Join-Path $ProjectRoot "output\video"
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$Segments = @(
    "Ravi changed jobs. His previous provident fund account is not available to transfer, but that message does not say what to inspect.",
    "ClaimPath checks one documented prerequisite using fictional records. It finds that the previous employment has no Date of Exit.",
    "The visible name variation is not the blocker in this fixture. The rule, original value, source, and uncertainty stay inspectable.",
    "The demo adds only the missing Date of Exit and recomputes the same checks. No EPFO account is changed.",
    "The prerequisite is now met in the simulation. ClaimPath points to EPFO's Mark Exit route before Ravi retries the transfer.",
    "The core is deterministic: fictional evidence, a versioned published prerequisite, counterfactual recomputation, and an official handoff.",
    "It asks for no UAN, Aadhaar, PAN, OTP, or document. It makes no government API call and never claims approval.",
    "The same focused journey works in Hindi, on a small screen, with keyboard semantics and no artificial intelligence dependency.",
    "When EPFO guidance changes, the product must fail safely and send the citizen to the current official route.",
    "ClaimPath removes one hidden prerequisite, without pretending to be EPFO."
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
