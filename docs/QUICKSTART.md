# Quickstart — Open Hoops

> Get the local Open Hoops dev stack running from a fresh clone.
> Estimated time: 15–30 minutes (includes Ollama model download).

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Docker Desktop | 24+ | Enable WSL2 backend on Windows |
| WSL2 + Ubuntu 22.04 | — | **Required on Windows.** See below. |
| Git | 2.40+ | For cloning |
| 50 GB free disk space | — | Docker images + MinIO data + Ollama model |

---

## 1. Windows: Set Up WSL2

> **Skip this section if you are on Linux or macOS.**

```powershell
# Run in PowerShell (Administrator)
wsl --install -d Ubuntu-22.04
wsl --set-default-version 2
```

Restart your machine after WSL2 installs. Then open the **Ubuntu 22.04** app from the Start menu and complete the Linux user setup.

In Docker Desktop:
1. Settings → General → Enable **"Use the WSL 2 based engine"**
2. Settings → Resources → WSL Integration → Enable for Ubuntu-22.04

**Clone the repo inside WSL2's Linux filesystem:**
```bash
# In the WSL2 Ubuntu terminal
cd ~
git clone https://github.com/hamidz/open-hoops.git
cd open-hoops
```

> ⚠️ Do not clone into `/mnt/c/Users/...`. Windows filesystem mounts have slow I/O inside Docker containers, which will severely impact video processing performance.

---

## 2. Clone the Repository

```bash
# Linux / macOS / WSL2
git clone https://github.com/hamidz/open-hoops.git
cd open-hoops
```

---

## 3. Configure Environment

```bash
cp .env.example .env
```

Open `.env` in a text editor and set at minimum:

```bash
POSTGRES_PASSWORD=<choose a strong password>
MINIO_ROOT_PASSWORD=<choose a strong password, min 8 chars>
```

The defaults for everything else are fine for local development.

---

## 4. Run Setup

```bash
./scripts/setup.sh
```

This will:
- Validate your `.env`
- Build and start all Docker containers
- Create MinIO storage buckets
- Download the default Ollama LLM model (`llama3.1:8b`, ~4.7 GB — may take a few minutes)

---

## 5. Verify Everything Is Running

```bash
./scripts/check_health.sh
```

Expected output:
```
  ✓ API (FastAPI)
  ✓ Frontend (Next.js)
  ✓ MinIO API
  ✓ MinIO Console
  ✓ Ollama
  ✓ PostgreSQL (via Docker)
  ✓ Redis (via Docker)

All 7 checks passed.
```

If any check fails, see the **Troubleshooting** section below.

---

## 6. Open the App

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API | http://localhost:8000/api/v1/health |
| API Docs (Swagger) | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |


---

## 7. Run Your First Workflow

1. Open http://localhost:3000.
2. Click **Start first workflow** or go directly to http://localhost:3000/upload.
3. Upload an `.mp4` or `.mov` basketball clip and optionally add a label.
4. After upload, Open Hoops redirects to the job detail page. The MVP marks the job complete and shows generated first-pass player/team stats.
5. Return to http://localhost:3000/dashboard to review uploaded jobs.

> Current MVP note: stats are generated from a deterministic mock analytics pipeline so the full local workflow is usable before the real CV engine phases are complete.

---

## 8. Seed Mock Data (Optional)

After Phase 03 is implemented, you can seed the dashboard with synthetic data:

```bash
make seed
# or:
python scripts/generate_mock_data.py
```

---

## AMD ROCm GPU Acceleration (Windows/Linux — AMD GPU)

If you have an AMD RDNA2/RDNA3 GPU (e.g., RX 7000 / RX 9000 series) and want hardware-accelerated CV processing:

### Verify ROCm in WSL2

```bash
# In WSL2 Ubuntu terminal
rocm-smi --showproductname
# Should list your GPU

ls /dev/kfd /dev/dri
# Should show these devices
```

If `rocm-smi` is not found, install ROCm:
```bash
# Install ROCm 6.x on Ubuntu 22.04
sudo apt install -y "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
sudo apt install -y rocm
```

### Start Stack with GPU

```bash
make dev-gpu
# or:
docker compose -f infra/docker-compose.yml -f infra/docker-compose.gpu.yml up -d
```

### RDNA3 Compatibility Note

Some RDNA3 cards (gfx1100) require an override for full ROCm compatibility. If you experience issues, add to `.env`:

```bash
HSA_OVERRIDE_GFX_VERSION=11.0.0
```

---

## Common Commands

```bash
make dev          # Start stack (CPU)
make dev-gpu      # Start stack (AMD ROCm GPU)
make stop         # Stop all containers
make logs         # Tail all logs
make health       # Check service health
make test         # Run all tests
make lint         # Run all linters
make build        # Rebuild Docker images
make clean        # Remove containers + volumes (DESTRUCTIVE)
```

---

## Troubleshooting

### "POSTGRES_PASSWORD is required" error

You haven't set `POSTGRES_PASSWORD` in `.env`. Edit the file and set a non-default value.

### MinIO not healthy

Check MinIO logs: `docker compose -f infra/docker-compose.yml logs minio`

Ensure `MINIO_ROOT_PASSWORD` is at least 8 characters.

### Ollama model pull failed

Pull manually:
```bash
docker compose -f infra/docker-compose.yml exec ollama ollama pull llama3.1:8b
```

### cv_worker not processing jobs (ROCm)

Check that `/dev/kfd` exists in WSL2:
```bash
ls -la /dev/kfd /dev/dri
```

If missing, ROCm drivers may not be loaded. See: [ROCm WSL2 install guide](https://rocm.docs.amd.com/en/latest/how-to/wsl2/index.html).

### Docker volume data lost

Never run `docker compose down -v` unless you intentionally want to delete all data. Use `docker compose down` (without `-v`) to stop containers while preserving volumes.

### Windows filesystem performance

If processing is slow, ensure you cloned inside WSL2's Linux filesystem (`~/open-hoops`), not on a Windows path (`/mnt/c/...`).

---

## Data Privacy Note

Open Hoops processes basketball video locally. No video, analytics data, or player information leaves your machine. The only outbound network requests are:
- Pulling Docker images (setup only)
- Pulling the Ollama model (setup only)

You are responsible for obtaining consent from all individuals appearing in footage before processing. See `docs/SECURITY_PRIVACY.md` for the full privacy policy.
