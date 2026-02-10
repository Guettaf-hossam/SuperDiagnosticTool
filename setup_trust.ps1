# PowerShell script to create a self-signed certificate and sign the executable
# Run this as Administrator

$CertName = "Hossam Guettaf - Open Source"
$ExePath = "dist\SuperDiagnosticTool.exe"

# 1. Check if certificate exists, if not create it
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -match $CertName }

if (-not $cert) {
    Write-Host "Creating self-signed code signing certificate..." -ForegroundColor Cyan
    $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=$CertName" -CertStoreLocation Cert:\CurrentUser\My
    Write-Host "Certificate created: $($cert.Thumbprint)" -ForegroundColor Green
} else {
    Write-Host "Using existing certificate: $($cert.Thumbprint)" -ForegroundColor Yellow
}

# 2. Export certificate to trusted root (optional, for local machine trust)
# This prevents "Untrusted Publisher" on your OWN machine
Write-Host "Exporting public certificate..." -ForegroundColor Cyan
$CertPath = "SuperDiagnosticTool_Cert.cer"
Export-Certificate -Cert $cert -FilePath $CertPath -Force
Write-Host "Certificate exported to: $CertPath" -ForegroundColor Green

Write-Host "Installing certificate to Trusted Root (Requires Admin)..." -ForegroundColor Cyan
try {
    Import-Certificate -FilePath $CertPath -CertStoreLocation Cert:\CurrentUser\Root
    Write-Host "Certificate installed to Trusted Root." -ForegroundColor Green
} catch {
    Write-Host "Failed to install certificate to Trusted Root. You may need to run as Administrator manually." -ForegroundColor Red
}

# 3. Sign the Executable
if (Test-Path $ExePath) {
    Write-Host "Signing $ExePath..." -ForegroundColor Cyan
    Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert
    
    $sig = Get-AuthenticodeSignature -FilePath $ExePath
    if ($sig.Status -eq 'Valid') {
        Write-Host "SUCCESS: Executable successfully signed!" -ForegroundColor Green
        Write-Host "Signature: $($sig.SignerCertificate.Subject)"
    } else {
        Write-Host "ERROR: Signing failed. Status: $($sig.Status)" -ForegroundColor Red
        Write-Host "Message: $($sig.StatusMessage)" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Executable not found at $ExePath. Build it first!" -ForegroundColor Red
}

Write-Host "`nDONE. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
