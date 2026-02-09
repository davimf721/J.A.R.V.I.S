# JARVIS - Script de Inicializacao para Windows
# Uso: .\init-windows.ps1

param(
    [switch]$SkipValidation = $false,
    [switch]$Force = $false
)

$ErrorActionPreference = "Continue"
$script:StartTime = Get-Date

function Get-ElapsedTime {
    $elapsed = (Get-Date) - $script:StartTime
    return "[{0:D2}:{1:D2}:{2:D2}]" -f $elapsed.Hours, $elapsed.Minutes, $elapsed.Seconds
}

function Write-Status { Write-Host "[*] $(Get-ElapsedTime) $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "[+] $(Get-ElapsedTime) $args" -ForegroundColor Green }
function Write-Warn { Write-Host "[!] $(Get-ElapsedTime) $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[-] $(Get-ElapsedTime) $args" -ForegroundColor Red }
function Write-Section { Write-Host "`n=== $args ===" -ForegroundColor Magenta }

function Print-Banner {
    Write-Host ""
    Write-Host "=================================================" -ForegroundColor Cyan
    Write-Host "  JARVIS - Windows Initialization Script" -ForegroundColor Cyan
    Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    Write-Host "=================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Validate-Environment {
    Write-Section "Validacao de Ambiente"
    
    Write-Status "Verificando Docker..."
    try {
        $dockerVersion = docker --version 2>$null
        Write-Success "Docker encontrado: $dockerVersion"
    } catch {
        Write-Error "Docker nao encontrado ou nao esta rodando"
        Write-Warn "Solucao: Inicie Docker Desktop"
        return $false
    }
    
    Write-Status "Verificando docker-compose..."
    try {
        $composeVersion = docker-compose --version 2>$null
        Write-Success "docker-compose encontrado: $composeVersion"
    } catch {
        Write-Error "docker-compose nao encontrado"
        Write-Warn "Solucao: Atualize Docker Desktop para incluir docker-compose"
        return $false
    }
    
    Write-Status "Verificando docker-compose.yml..."
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "docker-compose.yml nao encontrado"
        return $false
    }
    Write-Success "docker-compose.yml encontrado"
    
    return $true
}

function Check-DiskSpace {
    Write-Section "Verificacao de Espaco em Disco"
    
    $disk = Get-Volume | Where-Object { $_.DriveLetter -eq "C" }
    $freeGBs = [math]::Round($disk.SizeRemaining / 1GB, 2)
    $totalGBs = [math]::Round($disk.Size / 1GB, 2)
    $percentFree = [math]::Round(($freeGBs / $totalGBs) * 100, 2)
    
    Write-Status "Espaco disponivel: $freeGBs GB de $totalGBs GB ($percentFree%)"
    
    if ($percentFree -lt 5) {
        Write-Error "CRITICO: Menos de 5% de espaco livre"
        Write-Error "Build nao sera possivel nestes condicoes"
        return $false
    } elseif ($percentFree -lt 20) {
        Write-Warn "ALERTA: Menos de 20% de espaco livre"
        Write-Warn "Build pode falhar se espaco nao for liberado"
        
        if (-not $Force) {
            Write-Host ""
            $response = Read-Host "Continuar mesmo assim? (s/n)"
            if ($response -ne "s") {
                return $false
            }
        }
    } else {
        Write-Success "Espaco adequado para build"
    }
    
    return $true
}

function Start-Services {
    Write-Section "Inicializacao de Servicos"
    
    Write-Status "Limpando containers antigos..."
    docker-compose down -v --remove-orphans 2>$null
    Write-Success "Containers antigos removidos"
    
    Write-Host ""
    Write-Warn "ATENCAO: Isto pode levar 10-20 minutos na primeira vez"
    Write-Status "Iniciando servicos com: docker-compose up -d --build"
    Write-Host ""
    
    # Executar docker-compose
    $process = Start-Process -FilePath "docker-compose" `
                             -ArgumentList "up", "-d", "--build" `
                             -PassThru -NoNewWindow -ErrorAction Stop
    
    Write-Status "Aguardando conclusao do build..."
    $process.WaitForExit()
    
    Write-Host ""
    
    if ($process.ExitCode -eq 0) {
        Write-Success "Build completo com sucesso!"
        return $true
    } else {
        Write-Error "Build falhou com codigo: $($process.ExitCode)"
        Write-Status "Verificando logs..."
        docker-compose logs --tail=20
        return $false
    }
}

function Verify-Services {
    Write-Section "Verificacao dos Servicos"
    
    Write-Status "Aguardando 30 segundos para servicos ficarem prontos..."
    
    # Barra de progresso
    for ($i = 0; $i -lt 30; $i++) {
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 1
    }
    Write-Host ""
    Write-Host ""
    
    Write-Status "Status dos containers:"
    Write-Host ""
    docker-compose ps
    Write-Host ""
    
    $services = @(
        @{ name = "llm-service"; port = 8001 },
        @{ name = "news-service"; port = 8002 },
        @{ name = "memory-service"; port = 8005 },
        @{ name = "orchestrator"; port = 8010 }
    )
    
    $healthy = 0
    foreach ($svc in $services) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($svc.port)/health" `
                                        -ErrorAction SilentlyContinue -TimeoutSec 2
            
            if ($response.StatusCode -eq 200) {
                Write-Success "$($svc.name):$($svc.port) - HEALTHY"
                $healthy++
            }
        } catch {
            Write-Warn "$($svc.name):$($svc.port) - Ainda inicializando..."
        }
    }
    
    Write-Host ""
    Write-Status "Servicos saudaveis: $healthy/$($services.Count)"
    
    return $true
}

function Show-NextSteps {
    Write-Section "Proximos Passos"
    
    Write-Host "Monitore o progresso com:" -ForegroundColor Green
    Write-Host "  docker-compose logs -f" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Comandos uteis:" -ForegroundColor Green
    Write-Host "  docker-compose ps          # Ver status" -ForegroundColor Gray
    Write-Host "  docker-compose logs [svc]  # Ver logs de um servico" -ForegroundColor Gray
    Write-Host "  docker-compose down        # Parar tudo" -ForegroundColor Gray
    Write-Host "  docker-compose restart     # Reiniciar" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Acessar servicos:" -ForegroundColor Green
    Write-Host "  LLM Service:  http://localhost:8001/health" -ForegroundColor Gray
    Write-Host "  News Service: http://localhost:8002/health" -ForegroundColor Gray
    Write-Host "  Orchestrator: http://localhost:8010/health" -ForegroundColor Gray
    Write-Host ""
}

# ==================== MAIN ====================

Print-Banner

# Validacao
if (-not $SkipValidation) {
    if (-not (Validate-Environment)) {
        Write-Error "Validacao falhou. Abortando."
        exit 1
    }
} else {
    Write-Status "Saltando validacao (parametro -SkipValidation)"
}

# Espaco em disco
if (-not (Check-DiskSpace)) {
    Write-Error "Espaco insuficiente. Abortando."
    exit 1
}

# Inicializar
if (-not (Start-Services)) {
    Write-Error "Falha ao iniciar servicos. Abortando."
    exit 1
}

# Verificar
Verify-Services

# Sucesso
Write-Host ""
Write-Success "INICIALIZACAO COMPLETA!"
Show-NextSteps

Write-Status "Tempo total: $(Get-ElapsedTime)"
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Sistema pronto para uso" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
