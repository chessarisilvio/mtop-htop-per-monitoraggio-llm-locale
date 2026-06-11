# mtop

htop-like monitor for local LLM inference.

Provides real-time monitoring of GPU usage, memory, token generation speed, etc. for locally running LLMs.

## Descrizione

mtop è un tool di monitoraggio in tempo reale ispirato a htop, progettato specificamente per tenere traccia delle prestazioni di modelli linguistici locali (LLM) in esecuzione su GPU NVIDIA. Mostra utilizzo della GPU, memoria VRAM, temperatura e velocità di generazione token.

## Architettura

- **Linguaggio**: Python 3
- **Dipendenze**: curses (standard library), nvidia-smi (tool di sistema)
- **Componenti principali**:
  - `mtop.py`: Script principale con interfaccia curses
  - Funzione `get_gpu_stats()`: Esegue nvidia-smi per ottenere stats GPU
  - Funzione `get_token_rate()`: Placeholder per future integrazioni con metriche LLM
  - Loop principale con refresh configurabile e gestione interruzione Ctrl+C/q

## Installazione

1. Clonare o copiare la directory del progetto
2. Assicurarsi di avere nvidia-smi disponibile (driver NVIDIA installati)
3. Il script utilizza solo la libreria standard Python, nessuna dipendenza esterna richiesta

```bash
# Copia lo script in una directory nel tuo PATH (opzionale)
cp mtop.py ~/.local/bin/mtop
chmod +x ~/.local/bin/mtop
```

## Uso

```bash
./mtop.py [opzioni]
```

Opzioni disponibili:
- `--interval FLOAT`: Intervallo di aggiornamento in secondi (default: 1.0)
- `--gpu-id INT`: ID della GPU da monitorare (default: 0)
- `--llm-endpoint STRING`: Endpoint per metriche LLM (default: http://localhost:8080)
- `--no-color`: Disabilita output colorato

Esempi:
```bash
# Monitoraggio base della GPU 0
./mtop.py

# Monitoraggio della GPU 1 con aggiornamento ogni 0.5 secondi
./mtop.py --gpu-id 1 --interval 0.5

# Monitoraggio con endpoint LLM personalizzato
./mtop.py --llm-endpoint http://localhost:8090/metrics
```

## Esempi di output

```
mtop - Local LLM Monitor
========================
Update interval: 1.0s | GPU ID: 0 | LLM Endpoint: http://localhost:8080
----------------------------------------
GPU Usage:
  Utilization: 45.0%
  Memory: 2048 MB / 8192 MB
  Temperature: 55°C
Token Rate:
  Tokens/s: 42.3
  Prompt tokens: 1250
  Generation tokens: 3420
  Total tokens: 4670
Press 'q' or Ctrl+C to exit
```

## Stato

✅ COMPLETATO — 2026-06-10
- Implementazione core con monitoraggio GPU tramite nvidia-smi
- Interfaccia tempo reale con libreria curses
- Visualizzazione utilizzo GPU, memoria VRAM e temperatura
- Placeholder per integrazione futura con metriche token LLM
- Gestione interruzione pulita (Ctrl+C o 'q')
- Configurabile tramite argomenti della riga di comando