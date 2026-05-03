"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { API_URL } from "@/lib/api";
import { Card, Shell } from "@/components/ui";

const MAX_SIZE = 4 * 1024 * 1024 * 1024;

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [label, setLabel] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  function choose(nextFile: File | undefined) {
    setError(null);
    if (!nextFile) return;
    const name = nextFile.name.toLowerCase();
    if (!name.endsWith(".mp4") && !name.endsWith(".mov")) {
      setError("Upload an .mp4 or .mov video.");
      return;
    }
    if (nextFile.size > MAX_SIZE) {
      setError("Video exceeds the 4 GB MVP upload limit.");
      return;
    }
    setFile(nextFile);
  }

  function submit() {
    if (!file) {
      setError("Choose a video first.");
      return;
    }
    setUploading(true);
    setError(null);
    const form = new FormData();
    form.append("video", file);
    form.append("label", label);
    form.append("sport", "basketball");
    // Fetch does not expose upload progress events; XHR keeps the MVP progress bar accurate.
    const request = new XMLHttpRequest();
    request.upload.onprogress = (event) => {
      if (event.lengthComputable) setProgress(Math.round((event.loaded / event.total) * 100));
    };
    request.onload = () => {
      setUploading(false);
      if (request.status >= 200 && request.status < 300) {
        const body = JSON.parse(request.responseText) as { job_id: string };
        router.push(`/dashboard/jobs/${body.job_id}`);
      } else {
        setError(request.responseText || `Upload failed (${request.status})`);
      }
    };
    request.onerror = () => {
      setUploading(false);
      setError("Upload failed. Is the API running on port 8000?");
    };
    request.open("POST", `${API_URL}/api/v1/jobs/upload`);
    request.send(form);
  }

  return (
    <Shell>
      <div className="mx-auto max-w-2xl">
        <h1 className="text-4xl font-black">Upload video</h1>
        <p className="mt-2 text-foreground/70">Single-POST MVP upload for MP4/MOV clips. Stats are generated immediately for the first workflow.</p>
        <Card className="mt-6 space-y-5">
          <label className="block">
            <span className="text-sm font-bold">Label</span>
            <input className="mt-2 w-full rounded-xl border border-line bg-panel-soft px-4 py-3 outline-none focus:border-accent" value={label} onChange={(event) => setLabel(event.target.value)} placeholder="e.g. Varsity scrimmage Q1" />
          </label>
          <div onDrop={(event) => { event.preventDefault(); choose(event.dataTransfer.files[0]); }} onDragOver={(event) => event.preventDefault()} className="rounded-2xl border-2 border-dashed border-line bg-panel-soft p-8 text-center">
            <p className="font-bold">Drag and drop a video here</p>
            <p className="mt-1 text-sm text-foreground/60">or use the file picker</p>
            <input className="mt-5" type="file" accept=".mp4,.mov,video/mp4,video/quicktime" onChange={(event) => choose(event.target.files?.[0])} />
            {file && <p className="mt-4 font-mono text-sm text-accent">{file.name} · {(file.size / 1024 / 1024).toFixed(2)} MB</p>}
          </div>
          {uploading && <div className="h-3 overflow-hidden rounded-full bg-panel-soft"><div className="h-full bg-accent" style={{ width: `${progress}%` }} /></div>}
          {error && <p className="rounded-xl bg-danger/10 p-3 text-danger">{error}</p>}
          <button onClick={submit} disabled={uploading} className="w-full rounded-full bg-accent px-5 py-3 font-black text-black disabled:opacity-50">{uploading ? `Uploading ${progress}%` : "Upload and get stats"}</button>
        </Card>
      </div>
    </Shell>
  );
}
