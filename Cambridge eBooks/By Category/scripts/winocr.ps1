# Windows built-in OCR (Windows.Media.Ocr). Run with Windows PowerShell 5.1:
#   powershell -File winocr.ps1 <out_dir> <img1.png> [img2.png ...]
# Writes <out_dir>/<img basename>.json : [{x,y,w,h,text,words:[{x,y,w,h,t}]}] per line.
param([string]$OutDir, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Images)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, $type) { $t = $asTaskGeneric.MakeGenericMethod($type).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result }
[void][Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]
[void][Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
[void][Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('en-US'))
if (-not $engine) { $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }
foreach ($img in $Images) {
  $full = (Resolve-Path $img).Path
  $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($full)) ([Windows.Storage.StorageFile])
  $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $dec = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bmp = Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
  $lines = foreach ($ln in $res.Lines) {
    $ws = foreach ($w in $ln.Words) { $r = $w.BoundingRect; [pscustomobject]@{x=[int]$r.X; y=[int]$r.Y; w=[int]$r.Width; h=[int]$r.Height; t=$w.Text} }
    $x0 = ($ws | % x | Measure -Min).Minimum; $y0 = ($ws | % y | Measure -Min).Minimum
    $x1 = ($ws | % { $_.x + $_.w } | Measure -Max).Maximum; $y1 = ($ws | % { $_.y + $_.h } | Measure -Max).Maximum
    [pscustomobject]@{x=$x0; y=$y0; w=$x1-$x0; h=$y1-$y0; text=$ln.Text; words=@($ws)}
  }
  $stream.Dispose()
  $name = [IO.Path]::GetFileNameWithoutExtension($full)
  ConvertTo-Json -InputObject @($lines) -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $OutDir "$name.json")
  Write-Output "$name : $(@($lines).Count) lines"
}
