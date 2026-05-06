#  AI CCTV System — with Supabase Alert Logging

An AI-powered surveillance system using **YOLOv8** that detects persons in a video feed, monitors a restricted zone, and raises alerts for **intrusion**, **crowd**, and **fight** events — with a beep alarm and database logging.

---

##  Project Structure

```
ai-cctv-system/
├── app/
│   ├── main.py          # Core detection loop
│   ├── database.py      # Supabase alert logging
│   ├── dashboard.py     # Streamlit alerts dashboard
│   └── detector.py      # (reserved)
├── alarm.wav
├── yolov8n.pt           # YOLOv8 nano weights
├── test.mp4             # Sample test video
├── .env                 # Supabase credentials (never commit)
├── requirements.txt
└── README.md
```

---

##  What It Does

- Runs YOLOv8 on each frame to detect **persons** (COCO class 0)
- Draws a **restricted zone** (centre 40% of the frame) and triggers an **intrusion alert** if a person enters it
- Triggers a **crowd alert** if 3 or more people are detected simultaneously
- Triggers a **fight alert** based on rapid movement (displacement > 20px) or persons being too close together (distance < 50px)
- Beeps via `winsound` and logs every alert to **Supabase** (`alerts` table) via `insert_alert(type, count)` with a 5-second cooldown
- **Streamlit dashboard** (`dashboard.py`) reads alerts from Supabase and auto-refreshes every 5 seconds
- Loops the video back to frame 0 when it ends

---

##  Requirements

```
ultralytics
opencv-python
supabase
python-dotenv
streamlit
streamlit-autorefresh
pandas
winsound        # built-in on Windows
```

```bash
pip install ultralytics opencv-python supabase python-dotenv streamlit streamlit-autorefresh pandas
```

> `winsound` is built into Windows — no install needed. On Linux/macOS see [Troubleshooting](#troubleshooting).

---

##  Running

```bash
python app/main.py
```

Press **ESC** to quit.

---

##  Key Settings (in `main.py`)

| Variable | Default | Description |
|---|---|---|
| `VIDEO_PATH` | `"test.mp4"` | Video source |
| `ALERT_COOLDOWN` | `5` | Seconds between alerts |
| `CROWD_THRESHOLD` | `3` | Person count to trigger crowd alert |
| Confidence | `0.4` | Passed to `model()` |

---

##  Using with a Live CCTV / IP Camera

The system reads from `test.mp4` by default. To switch to a **live RTSP camera**, make two changes in `main.py`:

**Step 1 — Replace the video source**

```python
RTSP_URL = "rtsp://username:password@192.168.1.100:554/stream1"
cap = cv2.VideoCapture(RTSP_URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
```

**Step 2 — Replace the loop-back with reconnection logic**

```python
if not ret:
    cap.release()
    time.sleep(3)
    cap = cv2.VideoCapture(RTSP_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    continue
```

Everything else — detection, alerts, database logging — works unchanged.

### Common RTSP URL formats

| Brand | URL |
|---|---|
| Hikvision | `rtsp://admin:pass@192.168.1.x:554/Streaming/Channels/101` |
| Dahua | `rtsp://admin:pass@192.168.1.x:554/cam/realmonitor?channel=1&subtype=0` |
| Reolink | `rtsp://admin:pass@192.168.1.x:554/h264Preview_01_main` |
| TP-Link Tapo | `rtsp://username:pass@192.168.1.x:554/stream1` |

> Verify your URL with **VLC → Open Network Stream** before running.

---

##  Streamlit Dashboard

`app/dashboard.py` is a **read-only monitoring dashboard** — it does not run the camera. Run it alongside `main.py` to monitor alerts in the browser in real time.

**What it shows:**

- Sidebar filters by **event type** (intrusion / crowd / fight), **time range**, and **record limit**
- Filtered alerts table
- Metric cards — total intrusion, crowd, and fight counts for the filtered view
- Bar chart of event distribution
- **Recent alerts** — events from the last 60 seconds highlighted separately
- Auto-refreshes every **5 seconds** via `streamlit-autorefresh`

**Run it:**

```bash
streamlit run app/dashboard.py
```

Opens at **http://localhost:8501**. To access from another device on your network:

```bash
streamlit run app/dashboard.py --server.address 0.0.0.0
```

> The dashboard reads directly from the Supabase `alerts` table, so it reflects detections from `main.py` in near real time.

---

##  Database — Supabase

All alerts are logged to a **Supabase** PostgreSQL table in real time via `app/database.py`.

### Table schema (`alerts`)

| Column | Type | Description |
|---|---|---|
| `id` | int8 (auto) | Primary key |
| `event_type` | text | `"intrusion"`, `"crowd"`, or `"fight"` |
| `person_count` | int4 | Number of persons detected at alert time |
| `created_at` | timestamptz (auto) | Timestamp set by Supabase |

Create this table in your Supabase SQL editor:

```sql
create table alerts (
  id bigint generated always as identity primary key,
  event_type text not null,
  person_count int not null,
  created_at timestamptz default now()
);
```

### How it works

`insert_alert(event_type, person_count)` in `main.py` is called whenever an alert fires (subject to the 5-second cooldown). It inserts one row per alert type — so a single frame can log up to three rows if intrusion + crowd + fight all trigger together.

###  Securing your credentials

The current `database.py` has the Supabase URL and key hardcoded. **Do not commit this to a public repo.** Use a `.env` file instead:

1. Create `.env` in the project root:
```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

2. Update `database.py`:
```python
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def insert_alert(event_type, person_count):
    supabase.table("alerts").insert({"event_type": event_type, "person_count": person_count}).execute()
```

3. Add `.env` to `.gitignore`:
```
.env
```

Install the dependency:
```bash
pip install python-dotenv
```

---

##  Troubleshooting

**`winsound` not available (Linux/macOS)** — replace `winsound.Beep(1000, 300)` in `main.py` with:
```python
import pygame
pygame.mixer.init()
pygame.mixer.Sound("alarm.wav").play()
```
Then `pip install pygame`.

**RTSP stream won't connect** — test the URL in VLC first and make sure port `554` is open on your network.

**High CPU on live stream** — add `if frame_count % 2 != 0: continue` to skip every other frame.

---

##  License

Open source. See [LICENSE](LICENSE) for details.
