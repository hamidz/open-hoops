# Security, Privacy, and Data Handling — Open Hoops

> Planning-stage security and privacy requirements for a local-first basketball video analytics platform.

---

## 1. Security Posture

Open Hoops MVP is designed as a local, single-user, self-hosted application. The default threat model assumes the user runs the stack on a trusted machine or trusted local network. This does not remove the need for careful secret handling, safe file processing, and explicit data boundaries.

---

## 2. Sensitive Data

| Data | Sensitivity | Handling Requirement |
|---|---|---|
| Uploaded game videos | High | Store locally in MinIO; do not send to cloud services by default |
| Frame images / debug artifacts | High | Treat as derived video data; same controls as videos |
| Player labels / names | Medium to high | Store locally; avoid requiring real names |
| Team colors / annotations | Medium | Store locally with job artifacts |
| Analytics summaries | Medium | May reveal player behavior; store locally |
| LLM reports | Medium | Generated locally; no external model APIs for MVP |
| Logs | Medium | Must not include secrets or full raw payload dumps |

Videos may include minors. The project must treat all video-derived artifacts as private by default.

---

## 3. Data Boundary

```text
Browser
  ↕ local HTTP
FastAPI
  ↕ local Docker network
PostgreSQL / Redis / MinIO / Workers / Ollama
```

Default MVP boundary:

- No external cloud processing.
- No external LLM APIs.
- No telemetry/analytics sent to third-party services.
- Internet access may be needed during setup for container images and model downloads only.

---

## 4. Threat Model

| Threat | Risk | MVP Mitigation |
|---|---|---|
| Secret committed to repo | Credential exposure | `.env` ignored; examples only contain placeholders |
| Raw MinIO credentials exposed to frontend | Artifact compromise | API provides proxied or pre-signed access only |
| Malicious file upload | Worker crash or resource exhaustion | Validate extension, size, metadata; process in worker; fail safely |
| Oversized upload | Disk exhaustion | Configurable max upload size; clear `413` response |
| Corrupt video | Worker crash | Catch decode errors, mark job failed, continue worker loop |
| Path traversal in filenames | Arbitrary object path | Ignore user filename for storage keys; use UUID prefixes |
| LLM hallucination | Misleading coaching advice | Ground prompt in analytics only; include confidence caveats |
| Logs reveal private data | Privacy leakage | Avoid logging raw frames, labels, secrets, signed URLs |
| Local network exposure | Unintended access | Bind services to localhost where possible; document trusted-network assumption |
| Container runs as root | Privilege escalation | Production images run as non-root users in Phase 12 |

---

## 5. Secret Management

- Commit `.env.example`; never commit `.env`.
- Generated MinIO credentials must be random in release setup.
- Do not hardcode access keys, passwords, tokens, or model service credentials.
- Do not print secrets in setup scripts or health checks.
- Rotate local credentials by regenerating `.env` and restarting the stack.

---

## 6. Upload Safety Requirements

- Accept only configured video extensions (`.mp4`, `.mov` for MVP).
- Enforce max upload size before and during upload where possible.
- Store uploads under UUID object keys, not raw filenames.
- Extract frame zero using safe temporary paths and delete temporary files after use.
- Treat media metadata as untrusted input.
- Mark jobs failed with a clear error instead of crashing services.

---

## 7. Artifact Access Requirements

- The frontend must not receive MinIO root credentials.
- API should either proxy artifacts or issue short-lived pre-signed URLs.
- Signed URLs must not be logged.
- Delete job must remove video, telemetry, debug frames, heatmaps, reports, and annotations for that job.

---

## 8. LLM Safety Requirements

- MVP uses local Ollama only.
- Prompt must instruct the model to use only provided analytics data.
- Report UI must show model name, generated timestamp, and confidence caveats.
- If tracking coverage is low, the report must say the analysis may be unreliable.
- If Ollama is unavailable, fail report generation gracefully.

---

## 9. Privacy Review Checklist

Before release:

- [ ] No external APIs are called during normal analysis.
- [ ] `.env` and local videos are ignored by git.
- [ ] Sample data is synthetic or explicitly approved for redistribution.
- [ ] Logs do not contain private filenames beyond necessary user-visible metadata.
- [ ] Delete job removes all associated artifacts.
- [ ] Quickstart explains that users are responsible for consent and lawful use of videos.

---

## 10. Post-MVP Security Work

- Authentication and local user accounts if the app is exposed beyond localhost.
- Role-based access control for team workspaces.
- Audit log for cloud or multi-user deployment.
- Malware scanning or deeper media sandboxing for untrusted uploads.
- TLS termination guidance for remote access.
- Configurable retention policy and secure delete workflow.
