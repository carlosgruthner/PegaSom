# Script PowerShell para instalar dependencias do PegaVideo
Write-Host "Iniciando instalacao das dependencias do PegaVideo..." -ForegroundColor Green

# Verifica se o Python esta instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python nao encontrado!" -ForegroundColor Red
    Write-Host "Por favor, instale o Python antes de continuar."
    Write-Host "Baixe em: https://www.python.org/downloads/"
    Pause
    exit
}

# Verifica se o pip esta instalado
try {
    $pipVersion = pip --version 2>&1
    Write-Host "Pip encontrado: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "Pip nao encontrado!" -ForegroundColor Red
    Write-Host "Tentando instalar o pip..."
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Pip instalado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Falha ao instalar o pip!" -ForegroundColor Red
        Pause
        exit
    }
}

# Atualiza o pip para a versao mais recente
Write-Host "Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -eq 0) {
    Write-Host "Pip atualizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Falha ao atualizar o pip, continuando com a versao atual..." -ForegroundColor Yellow
}

# Lista de dependencias para instalar
$dependencies = @(
    "tkinter",
    "yt-dlp",
    "customtkinter",
    "darkdetect",
    "pyinstaller",
)

# Instala cada dependencia
foreach ($dep in $dependencies) {
    Write-Host "Instalando $dep..." -ForegroundColor Yellow
    pip install $dep
    if ($LASTEXITCODE -eq 0) {
        Write-Host "$dep instalado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Falha ao instalar $dep!" -ForegroundColor Red
    }
}

Write-Host "Instalacao das dependencias concluida!" -ForegroundColor Green
Write-Host "Verificando versoes instaladas:" -ForegroundColor Yellow

# Mostra as versoes instaladas
foreach ($dep in $dependencies) {
    $version = pip show $dep | Select-String "Version"
    Write-Host "$version" -ForegroundColor Cyan
}

Write-Host "Instalacao concluida!" -ForegroundColor Green

Pause