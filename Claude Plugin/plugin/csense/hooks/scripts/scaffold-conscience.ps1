# Common Sense SessionStart hook — scaffolds the conscience on first run.
# Idempotent: does nothing if the brain already exists.

$BrainDir = Join-Path $HOME ".csense\conscience"
$TemplatesDir = "$env:CLAUDE_PLUGIN_ROOT\templates\founder"

if (Test-Path $BrainDir) {
    exit 0
}

New-Item -ItemType Directory -Path $BrainDir -Force
New-Item -ItemType Directory -Path (Join-Path $BrainDir "identity") -Force
New-Item -ItemType Directory -Path (Join-Path $BrainDir "governor") -Force
New-Item -ItemType Directory -Path (Join-Path $BrainDir "memory") -Force
New-Item -ItemType Directory -Path (Join-Path $BrainDir "feedback") -Force
New-Item -ItemType Directory -Path (Join-Path $BrainDir "inbox") -Force
New-Item -ItemType Directory -Path (Join-Path $BrainDir "research") -Force
New-Item -ItemType Directory -Path (Join-Path $BrainDir "logs") -Force

Copy-Item -Path "$TemplatesDir\identity\*" -Destination (Join-Path $BrainDir "identity") -Recurse -Force
Copy-Item -Path "$TemplatesDir\governor\*" -Destination (Join-Path $BrainDir "governor") -Recurse -Force
Copy-Item -Path "$TemplatesDir\memory\*"   -Destination (Join-Path $BrainDir "memory")   -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$TemplatesDir\feedback\*" -Destination (Join-Path $BrainDir "feedback") -Recurse -Force -ErrorAction SilentlyContinue

$Config = @{
    mode = "observe"
    version = "0.1.0"
    installed = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

$Config | Out-File -FilePath (Join-Path $BrainDir "config.json") -Encoding utf8

New-Item -ItemType File -Path (Join-Path $BrainDir "logs\action-log.jsonl") -Force

Write-Host "
  Common Sense v0.1.0 installed.
  Your conscience lives at ~/.csense/conscience/
  Edit any file in plain Markdown. Changes apply on the next tool call.

  Mode: observe (decisions logged, never enforced)
  Try: /csense-report after a few minutes of work
"
