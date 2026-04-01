# MeetRecord – AI Meeting Summarizer
## Running Locally in VS Code

This project has two parts:
- **backend/** — Express API server (Node.js + TypeScript)
- **frontend/** — React app (Vite + TailwindCSS)

---

## Prerequisites

- Node.js 18+ (https://nodejs.org)
- npm (comes with Node)
- PostgreSQL running locally (or a free cloud database like Neon.tech or Supabase)
- An OpenAI API key (https://platform.openai.com)

---

## Step 1 — Set up the Backend

```bash
cd backend
npm install
```

Copy the example env file and fill it in:

```bash
cp .env.example .env
```

Open `.env` and set these values:

```
DATABASE_URL=postgresql://user:password@localhost:5432/meeting_recorder
OPENAI_API_KEY=sk-your-real-key-here
PORT=3001
```

> **Tip:** If you don't have PostgreSQL locally, create a free database at https://neon.tech
> Your DATABASE_URL will look like: `postgresql://user:pass@ep-xxx.neon.tech/meeting_recorder?sslmode=require`

Create the database table:

```bash
npm run db:push
```

Start the backend:

```bash
npm run dev
```

You should see: `[Server] Running on http://localhost:3001`

---

## Step 2 — Set up the Frontend

In a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

You should see: `Local: http://localhost:5173`

Open http://localhost:5173 in your browser.

---

## How it works

1. Click the mic button to start recording
2. Audio is sent to the backend in 1-second chunks
3. When you stop, the backend runs the full pipeline:
   - **Whisper** (OpenAI) → speech-to-text transcription
   - **GPT-4o-mini** → speaker diarization (who said what)
   - **GPT-4o-mini** → meeting summary with key points & action items
4. Results appear in the tabbed panel

---

## Project Structure

```
backend/
  src/
    index.ts              ← Express server entry point
    db.ts                 ← Database schema (Drizzle ORM)
    routes/
      recording/
        index.ts          ← REST endpoints (/start, /chunk, /stop, /:id)
        pipeline.ts       ← AI processing pipeline (STT → Diarization → Summary)
        store.ts          ← In-memory audio chunk buffer

frontend/
  src/
    App.tsx               ← Router setup
    types.ts              ← Shared TypeScript types
    hooks/
      use-audio-recorder.ts  ← MediaRecorder + API integration hook
    components/
      Sidebar.tsx         ← Session history list
      ResultsPanel.tsx    ← Tabbed results (Summary / Speakers / Transcript)
      Waveform.tsx        ← Animated waveform bars
    pages/
      Home.tsx            ← Main recorder page
      SessionView.tsx     ← View a past session
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/recording/start | Create a new recording session |
| POST | /api/recording/:id/chunk | Upload an audio chunk (base64) |
| POST | /api/recording/:id/stop | Stop recording, start AI pipeline |
| GET  | /api/recording/:id | Get session status & results |
| GET  | /api/recording | List all sessions |
