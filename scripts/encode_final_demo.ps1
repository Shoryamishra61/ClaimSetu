$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$InputPath = Join-Path $ProjectRoot "output\video\identity-rescue-final-submission.webm"
$OutputPath = Join-Path $ProjectRoot "output\video\identity-rescue-final-submission.mp4"
$TemporaryPath = Join-Path $ProjectRoot "tmp\identity-rescue-final-submission.mp4"
New-Item -ItemType Directory -Path (Split-Path -Parent $TemporaryPath) -Force | Out-Null

$FfmpegPath = uvx --from imageio-ffmpeg python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
if (-not (Test-Path -LiteralPath $FfmpegPath)) { throw "FFmpeg binary unavailable" }

& $FfmpegPath -y -i $InputPath -t 118 -map 0:v:0 -map 0:a:0 `
    -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p `
    -c:a aac -b:a 128k -movflags +faststart $TemporaryPath
if ($LASTEXITCODE -ne 0) { throw "Final demo encoding failed" }

Copy-Item -LiteralPath $TemporaryPath -Destination $OutputPath -Force

# Extract deterministic review frames with FFmpeg. Browser seeking can capture a
# pre-decode white frame even when the encoded media is healthy.
foreach ($Second in @(3, 14, 26, 39, 52, 65, 77, 90, 103, 114)) {
    $FramePath = Join-Path $ProjectRoot "output\video\final-frame-$Second.png"
    & $FfmpegPath -loglevel error -y -ss $Second -i $OutputPath -frames:v 1 $FramePath
    if ($LASTEXITCODE -ne 0) { throw "Final demo frame extraction failed at $Second seconds" }
}
Write-Output "FINAL_MP4=$OutputPath"
