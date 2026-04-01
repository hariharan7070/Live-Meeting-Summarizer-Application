import streamlit as st
import openai
import tempfile
import os
import time
import wave
import numpy as np
import threading
from pathlib import Path
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
import io

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EchoMind — AI Transcription",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Instrument+Sans:wght@300;400;500&display=swap');

:root {
    --bg:       #06080d;
    --surface:  #0d1117;
    --card:     #111820;
    --border:   #1e2a38;
    --glow:     #0af;
    --glow2:    #f72585;
    --glow3:    #b5e853;
    --text:     #dce8f5;
    --muted:    #4a6080;
    --display:  'Syne', sans-serif;
    --body:     'Instrument Sans', sans-serif;
}

html, body, [class*="css"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--body) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 5rem !important; max-width: 1300px !important; }

/* ── Animated bg grid ── */
.bg-grid {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(0,170,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,170,255,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: var(--display);
    font-size: 0.7rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--glow);
    margin-bottom: 1rem;
}
.hero-title {
    font-family: var(--display);
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(135deg, #fff 30%, var(--glow) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
}
.hero-sub {
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto 2rem;
    line-height: 1.7;
}

/* ── API Key Input ── */
.stTextInput > div > div > input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Courier New', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--glow) !important;
    box-shadow: 0 0 0 2px rgba(0,170,255,0.15) !important;
}

/* ── Cards ── */
.echo-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.echo-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--glow), transparent);
    opacity: 0.4;
}
.card-label {
    font-family: var(--display);
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-label-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--glow);
    display: inline-block;
}

/* ── Status badge ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-family: var(--display);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.sp-idle    { background: rgba(74,96,128,0.15); color: var(--muted);  border: 1px solid #1e2a38; }
.sp-rec     { background: rgba(247,37,133,0.1); color: var(--glow2); border: 1px solid rgba(247,37,133,0.4); }
.sp-proc    { background: rgba(0,170,255,0.1);  color: var(--glow);  border: 1px solid rgba(0,170,255,0.4); }
.sp-done    { background: rgba(181,232,83,0.1); color: var(--glow3); border: 1px solid rgba(181,232,83,0.4); }
.pulse-dot {
    width: 6px; height: 6px; border-radius: 50%; display: inline-block;
}
.pd-idle { background: var(--muted); }
.pd-rec  { background: var(--glow2); animation: blink 1s infinite; }
.pd-proc { background: var(--glow); }
.pd-done { background: var(--glow3); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.15} }

/* ── Transcript lines ── */
.tx-wrap {
    max-height: 420px;
    overflow-y: auto;
    padding-right: 0.3rem;
}
.tx-wrap::-webkit-scrollbar { width: 3px; }
.tx-wrap::-webkit-scrollbar-track { background: transparent; }
.tx-wrap::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.tx-line {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1rem;
    align-items: flex-start;
}
.tx-spk {
    font-family: var(--display);
    font-size: 0.62rem;
    font-weight: 700;
    padding: 0.22rem 0.6rem;
    border-radius: 5px;
    min-width: 72px;
    text-align: center;
    flex-shrink: 0;
    margin-top: 3px;
    letter-spacing: 0.05em;
}
.spk0 { background: rgba(0,170,255,0.12); color: #0af; border: 1px solid rgba(0,170,255,0.25); }
.spk1 { background: rgba(181,232,83,0.12); color: #b5e853; border: 1px solid rgba(181,232,83,0.25); }
.spk2 { background: rgba(247,37,133,0.12); color: #f72585; border: 1px solid rgba(247,37,133,0.25); }
.spk3 { background: rgba(255,190,0,0.12); color: #ffbe00; border: 1px solid rgba(255,190,0,0.25); }
.spk4 { background: rgba(130,80,255,0.12); color: #8250ff; border: 1px solid rgba(130,80,255,0.25); }

.tx-text {
    font-size: 0.93rem;
    line-height: 1.7;
    color: var(--text);
    flex: 1;
}
.tx-time {
    font-family: 'Courier New', monospace;
    font-size: 0.6rem;
    color: var(--muted);
    flex-shrink: 0;
    padding-top: 5px;
}

/* ── Summary ── */
.summary-body {
    font-size: 0.93rem;
    line-height: 1.85;
    color: var(--text);
    border-left: 2px solid var(--glow3);
    padding-left: 1.2rem;
    margin-top: 0.5rem;
}

/* ── Upload zone ── */
.stFileUploader > div {
    background: var(--card) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 14px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s !important;
}
.stFileUploader > div:hover {
    border-color: var(--glow) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: var(--display) !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.6rem !important;
    transition: all 0.2s ease !important;
    border: none !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--display) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--border) !important;
    color: var(--text) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem !important;
}

/* ── Metrics ── */
.m-grid {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 0.8rem;
    margin-bottom: 1.2rem;
}
.m-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.m-val {
    font-family: var(--display);
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--glow);
    display: block;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.m-lbl {
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-family: var(--display);
}

/* ── Progress ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--glow), var(--glow3)) !important;
    border-radius: 999px !important;
}
.stProgress > div > div > div {
    background: var(--border) !important;
    border-radius: 999px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--glow) !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* ── Alert ── */
.stAlert {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
</style>

<div class="bg-grid"></div>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────────
defaults = {
    "api_key": "",
    "transcript_lines": [],
    "summary": "",
    "status": "idle",
    "speakers": {},
    "processing": False,
    "raw_transcript": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

SPEAKER_CLASSES = ["spk0", "spk1", "spk2", "spk3", "spk4"]
SPEAKER_LABELS  = ["Speaker A", "Speaker B", "Speaker C", "Speaker D", "Speaker E"]

# ─── Helper Functions ─────────────────────────────────────────────────────────────

def transcribe_audio(audio_bytes, api_key, file_ext="wav"):
    """Transcribe audio using Whisper API with word-level timestamps."""
    client = openai.OpenAI(api_key=api_key)
    with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        with open(tmp_path, "rb") as af:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=af,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        return response
    finally:
        os.unlink(tmp_path)


def diarize_with_gpt(transcript_text, api_key):
    """Use GPT-4 to diarize speakers and structure transcript."""
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""You are an expert transcript analyst. Given this raw transcript, identify different speakers based on context, conversation flow, and speaking patterns. 

Label each segment as SPEAKER_A, SPEAKER_B, SPEAKER_C etc. Return ONLY a JSON array like:
[
  {{"speaker": "SPEAKER_A", "text": "...", "timestamp": "0:00"}},
  {{"speaker": "SPEAKER_B", "text": "...", "timestamp": "0:12"}}
]

If only one speaker is detected, still use SPEAKER_A for all segments.
Keep each segment to 1-3 sentences max.

Raw transcript:
{transcript_text}

Return ONLY valid JSON, no explanation."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    import json
    raw = response.choices[0].message.content
    # wrap if needed
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            # find the array inside
            for v in parsed.values():
                if isinstance(v, list):
                    return v
        return parsed
    except:
        return []


def generate_summary(transcript_lines, api_key):
    """Generate AI summary using GPT-4."""
    client = openai.OpenAI(api_key=api_key)
    transcript_text = "\n".join([f"{l['speaker']}: {l['text']}" for l in transcript_lines])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": f"""Analyze this transcript and provide:
1. **Meeting/Conversation Summary** (2-3 sentences overview)
2. **Key Points** (bullet points of main topics discussed)
3. **Action Items** (if any, with owner names)
4. **Speaker Insights** (brief note on each speaker's role/contribution)

Transcript:
{transcript_text}

Format your response in clean markdown."""
        }],
        temperature=0.4,
    )
    return response.choices[0].message.content


def process_audio(audio_bytes, api_key, file_ext="wav"):
    """Full pipeline: transcribe → diarize → summarize."""
    st.session_state.status = "transcribing"
    
    # Step 1: Whisper transcription
    result = transcribe_audio(audio_bytes, api_key, file_ext)
    
    # Build raw text
    if hasattr(result, 'segments') and result.segments:
        raw_text = " ".join([s.text.strip() for s in result.segments])
    else:
        raw_text = result.text if hasattr(result, 'text') else str(result)
    
    st.session_state.raw_transcript = raw_text
    st.session_state.status = "diarizing"
    
    # Step 2: GPT diarization
    diarized = diarize_with_gpt(raw_text, api_key)
    
    # Map speaker names
    speaker_map = {}
    idx = 0
    lines = []
    for seg in diarized:
        spk = seg.get("speaker", "SPEAKER_A")
        if spk not in speaker_map:
            speaker_map[spk] = idx
            idx = min(idx + 1, len(SPEAKER_LABELS) - 1)
        lines.append({
            "speaker": spk,
            "speaker_label": SPEAKER_LABELS[speaker_map[spk]],
            "speaker_class": SPEAKER_CLASSES[speaker_map[spk]],
            "text": seg.get("text", ""),
            "timestamp": seg.get("timestamp", ""),
        })
    
    st.session_state.transcript_lines = lines
    st.session_state.speakers = speaker_map
    st.session_state.status = "summarizing"
    
    # Step 3: GPT summary
    summary = generate_summary(lines, api_key)
    st.session_state.summary = summary
    st.session_state.status = "done"


# ─── HERO ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Powered by OpenAI Whisper + GPT-4</div>
    <div class="hero-title">EchoMind</div>
    <div class="hero-sub">Real-time AI transcription with speaker diarization and intelligent summaries</div>
</div>
""", unsafe_allow_html=True)

# ─── API KEY ─────────────────────────────────────────────────────────────────────
with st.container():
    col_key, col_space = st.columns([2, 2])
    with col_key:
        api_input = st.text_input(
            "🔑 OpenAI API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-proj-...",
            help="Get your key from platform.openai.com"
        )
        if api_input:
            st.session_state.api_key = api_input

api_ready = bool(st.session_state.api_key and st.session_state.api_key.startswith("sk-"))

if not api_ready:
    st.markdown("""
    <div style="background:rgba(247,37,133,0.08);border:1px solid rgba(247,37,133,0.25);
    border-radius:10px;padding:0.9rem 1.2rem;margin:1rem 0;font-size:0.85rem;color:#f72585;">
    ⚠️ Enter your OpenAI API key above to get started. Get one free at <strong>platform.openai.com</strong>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ─── STATUS BAR ──────────────────────────────────────────────────────────────────
status_map = {
    "idle":        ("sp-idle", "pd-idle", "Ready"),
    "recording":   ("sp-rec",  "pd-rec",  "Recording"),
    "transcribing":("sp-proc", "pd-proc", "Transcribing with Whisper"),
    "diarizing":   ("sp-proc", "pd-proc", "Identifying Speakers"),
    "summarizing": ("sp-proc", "pd-proc", "Generating Summary"),
    "done":        ("sp-done", "pd-done", "Complete"),
}
sc, dc, slabel = status_map.get(st.session_state.status, status_map["idle"])
st.markdown(f"""
<div style="margin-bottom:1.8rem">
    <span class="status-pill {sc}">
        <span class="pulse-dot {dc}"></span>
        {slabel}
    </span>
</div>
""", unsafe_allow_html=True)

# ─── MAIN TABS ───────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎙️  Record & Upload", "📊  Results"])

with tab1:
    input_col, info_col = st.columns([3, 2], gap="large")

    with input_col:
        mode = st.selectbox("Input Mode", ["🎤 Live Recording", "📁 Upload File"], label_visibility="collapsed")

        # ── LIVE RECORDING ──
        if "Live Recording" in mode:
            st.markdown('<div class="echo-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-label"><span class="card-label-dot"></span>Live Microphone</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <p style="font-size:0.85rem;color:var(--muted);margin-bottom:1rem;">
            Click the mic button below to start recording. Click again to stop and process.
            </p>
            """, unsafe_allow_html=True)

            audio_bytes = audio_recorder(
                text="",
                recording_color="#f72585",
                neutral_color="#0af",
                icon_name="microphone",
                icon_size="3x",
                pause_threshold=3.0,
                sample_rate=16000,
            )

            if audio_bytes and api_ready:
                st.session_state.status = "recording"
                st.success("✅ Recording captured! Processing now...")
                with st.spinner("Running AI pipeline..."):
                    try:
                        process_audio(audio_bytes, st.session_state.api_key, "wav")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.status = "idle"
            elif audio_bytes and not api_ready:
                st.warning("Please enter your OpenAI API key first!")

            st.markdown('</div>', unsafe_allow_html=True)

        # ── FILE UPLOAD ──
        else:
            st.markdown('<div class="echo-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-label"><span class="card-label-dot"></span>Upload Audio / Video</div>', unsafe_allow_html=True)

            uploaded = st.file_uploader(
                "Drop your file here",
                type=["mp3", "mp4", "wav", "m4a", "ogg", "webm", "flac", "mov", "avi", "mkv"],
                label_visibility="collapsed"
            )

            if uploaded:
                st.audio(uploaded)
                file_ext = uploaded.name.split(".")[-1].lower()

                # Convert video to audio if needed
                video_exts = ["mp4", "mov", "avi", "mkv", "webm"]
                
                btn_col, _ = st.columns([1, 2])
                with btn_col:
                    process_btn = st.button("⚡ Transcribe & Analyze", use_container_width=True, disabled=not api_ready)

                if process_btn and api_ready:
                    audio_data = uploaded.read()
                    
                    # Handle video files — extract audio via pydub
                    if file_ext in video_exts:
                        with st.spinner("Extracting audio from video..."):
                            try:
                                seg = AudioSegment.from_file(io.BytesIO(audio_data), format=file_ext)
                                buf = io.BytesIO()
                                seg.export(buf, format="mp3")
                                audio_data = buf.getvalue()
                                file_ext = "mp3"
                            except Exception as e:
                                st.error(f"Could not extract audio: {e}")
                                st.stop()

                    with st.spinner("Running AI pipeline — this may take a moment..."):
                        try:
                            process_audio(audio_data, st.session_state.api_key, file_ext)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            st.session_state.status = "idle"

            st.markdown('</div>', unsafe_allow_html=True)

    with info_col:
        st.markdown("""
        <div class="echo-card">
            <div class="card-label"><span class="card-label-dot"></span>How It Works</div>
            <div style="font-size:0.85rem;color:var(--muted);line-height:1.9">
                <div style="margin-bottom:0.9rem">
                    <span style="color:#0af;font-weight:600">① Whisper STT</span><br>
                    OpenAI's best-in-class speech recognition converts your audio to text with high accuracy.
                </div>
                <div style="margin-bottom:0.9rem">
                    <span style="color:#b5e853;font-weight:600">② Speaker Diarization</span><br>
                    GPT-4 intelligently identifies and separates different speakers in the conversation.
                </div>
                <div>
                    <span style="color:#f72585;font-weight:600">③ AI Summary</span><br>
                    GPT-4 generates a structured summary with key points and action items.
                </div>
            </div>
        </div>

        <div class="echo-card">
            <div class="card-label"><span class="card-label-dot"></span>Supported Formats</div>
            <div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-top:0.2rem">
                {badges}
            </div>
        </div>
        """.format(badges="".join([
            f'<span style="background:var(--surface);border:1px solid var(--border);border-radius:5px;padding:0.2rem 0.5rem;font-size:0.7rem;font-family:monospace;color:var(--muted)">{ext}</span>'
            for ext in ["mp3","mp4","wav","m4a","ogg","webm","flac","mov","avi","mkv"]
        ])), unsafe_allow_html=True)

with tab2:
    if not st.session_state.transcript_lines and st.session_state.status not in ["transcribing","diarizing","summarizing"]:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:var(--muted)">
            <div style="font-size:3rem;margin-bottom:1rem">🎙️</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.1rem;margin-bottom:0.5rem;color:var(--text)">No results yet</div>
            <div style="font-size:0.85rem">Record audio or upload a file to see the transcript and summary here</div>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.status in ["transcribing", "diarizing", "summarizing"]:
        labels = {"transcribing": (20, "Transcribing audio with Whisper..."),
                  "diarizing":    (60, "Identifying speakers with GPT-4..."),
                  "summarizing":  (85, "Generating AI summary...")}
        prog, msg = labels.get(st.session_state.status, (50, "Processing..."))
        st.markdown(f'<p style="color:var(--glow);font-size:0.88rem;font-family:Syne,sans-serif">{msg}</p>', unsafe_allow_html=True)
        st.progress(prog / 100)

    else:
        # ── Metrics ──
        n_speakers = len(set(l["speaker"] for l in st.session_state.transcript_lines))
        n_words = sum(len(l["text"].split()) for l in st.session_state.transcript_lines)
        n_segs = len(st.session_state.transcript_lines)

        st.markdown(f"""
        <div class="m-grid">
            <div class="m-box"><span class="m-val">{n_speakers}</span><span class="m-lbl">Speakers</span></div>
            <div class="m-box"><span class="m-val">{n_words}</span><span class="m-lbl">Words</span></div>
            <div class="m-box"><span class="m-val">{n_segs}</span><span class="m-lbl">Segments</span></div>
        </div>
        """, unsafe_allow_html=True)

        res_left, res_right = st.columns([3, 2], gap="large")

        with res_left:
            st.markdown('<div class="echo-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-label"><span class="card-label-dot"></span>Diarized Transcript</div>', unsafe_allow_html=True)
            st.markdown('<div class="tx-wrap">', unsafe_allow_html=True)

            for line in st.session_state.transcript_lines:
                st.markdown(f"""
                <div class="tx-line">
                    <span class="tx-spk {line['speaker_class']}">{line['speaker_label']}</span>
                    <span class="tx-text">{line['text']}</span>
                    <span class="tx-time">{line.get('timestamp','')}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div></div>', unsafe_allow_html=True)

            # Download transcript
            full_txt = "\n".join([f"[{l['speaker_label']}] {l['text']}" for l in st.session_state.transcript_lines])
            st.download_button("⬇ Download Transcript", full_txt, "transcript.txt", "text/plain")

        with res_right:
            st.markdown('<div class="echo-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-label"><span class="card-label-dot"></span>AI Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-body">', unsafe_allow_html=True)
            st.markdown(st.session_state.summary)
            st.markdown('</div></div>', unsafe_allow_html=True)

            # Speaker legend
            st.markdown('<div class="echo-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-label"><span class="card-label-dot"></span>Speakers Detected</div>', unsafe_allow_html=True)
            seen = {}
            for l in st.session_state.transcript_lines:
                spk = l["speaker"]
                if spk not in seen:
                    seen[spk] = {"label": l["speaker_label"], "cls": l["speaker_class"], "count": 0}
                seen[spk]["count"] += 1
            for spk, info in seen.items():
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem">
                    <span class="tx-spk {info['cls']}" style="margin:0">{info['label']}</span>
                    <span style="font-size:0.78rem;color:var(--muted)">{info['count']} segments</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Download summary
            st.download_button("⬇ Download Summary", st.session_state.summary, "summary.md", "text/markdown")

        # ── Reset ──
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        if st.button("↺ New Session"):
            for k in ["transcript_lines", "summary", "status", "speakers", "raw_transcript"]:
                st.session_state[k] = [] if k in ["transcript_lines", "speakers"] else "" if k in ["summary", "raw_transcript"] else "idle"
            st.rerun()
