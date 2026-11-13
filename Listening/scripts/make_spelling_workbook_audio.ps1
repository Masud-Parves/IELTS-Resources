# Make the dictation WAV files for the 7-Day Listening Spelling Mastery workbook.
# Usage: pwsh -File make_spelling_workbook_audio.ps1 [-Only day1,aw3]     (default: every set)
# Reads ../Spelling Workbook/dictation.json and writes ../Spelling Workbook/audio/*.wav (Windows text-to-speech).
param([string[]]$Only)
$Only = @($Only | ForEach-Object { $_ -split ',' } | Where-Object { $_ })   # -File passes "a,b" as one string
Add-Type -AssemblyName System.Speech
$root  = Join-Path $PSScriptRoot '..\Spelling Workbook'
$data  = Get-Content (Join-Path $root 'dictation.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$out   = Join-Path $root 'audio'
New-Item -ItemType Directory -Force $out | Out-Null
$names = @{ day1='Day1_Dictation'; day2='Day2_Dictation'; day3='Day3_Dictation'; day4='Day4_Dictation'
            day5='Day5_Dictation'; day6='Day6_Dictation'; day7='Day7_Dictation'; final='Final_Test_Dictation' }
foreach ($i in 1..7) { $names["aw$i"] = "AnswerWords_Block$i" }   # Real Answer Words blocks (word only)
$fmt   = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)

foreach ($key in $names.Keys) {
    if ($Only -and $key -notin $Only) { continue }
    $set = $data.$key
    if (-not $set) { continue }
    $wordOnly = -not ($set.items | Where-Object { $_[1] })
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    try { $synth.SelectVoice('Microsoft Zira Desktop') } catch {}
    $synth.Rate = -1
    $file = Join-Path $out ($names[$key] + '.wav')
    $synth.SetOutputToWaveFile($file, $fmt)
    $pb = New-Object System.Speech.Synthesis.PromptBuilder
    $pb.AppendText($set.title + '.')
    if ($set.gapped)   { $pb.AppendText('Each sentence is read twice. Write one word in each gap.') }
    elseif ($wordOnly) { $pb.AppendText('You will hear each word twice. Write the word.') }
    else               { $pb.AppendText('You will hear each word, a sentence, and the word again. Write the word.') }
    $pb.AppendBreak([TimeSpan]::FromSeconds(2))
    $n = 0
    foreach ($item in $set.items) {
        $n++
        $pb.AppendText("Number $n.")
        $pb.AppendBreak([TimeSpan]::FromMilliseconds(700))
        if ($set.gapped) {
            $pb.AppendText($item[1]); $pb.AppendBreak([TimeSpan]::FromSeconds(2))
            $pb.AppendText($item[1]); $pb.AppendBreak([TimeSpan]::FromSeconds(7))
        } else {
            $pb.AppendText($item[0] + '.'); $pb.AppendBreak([TimeSpan]::FromMilliseconds(1200))
            if ($item[1]) { $pb.AppendText($item[1]); $pb.AppendBreak([TimeSpan]::FromMilliseconds(800)) }
            $pb.AppendText($item[0] + '.'); $pb.AppendBreak([TimeSpan]::FromSeconds(6))
        }
    }
    $pb.AppendText('That is the end of the dictation. Now check your answers in the answer key.')
    $synth.Speak($pb)
    $synth.Dispose()
    Write-Output ("wrote {0}  ({1:N1} MB)" -f $file, ((Get-Item $file).Length / 1MB))
}
