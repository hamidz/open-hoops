# Open Hoops Web

Next.js frontend for the first-run Open Hoops workflow.

```bash
npm ci
npm run dev --workspace web -- --hostname 127.0.0.1 --port 3000
```

Open http://localhost:3000, upload an `.mp4` or `.mov`, then view generated stats.

Set `NEXT_PUBLIC_API_URL` when the API is exposed on a non-default port, especially for Docker builds where the value is baked into the frontend bundle.
