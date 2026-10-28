import tkinter as tk
import asyncio
import json
import threading
import time
import websockets

SCRIPT_BEATS = [
    ("3...", "#facc15"),
    ("2...", "#facc15"),
    ("1 — YOU ARE LIVE! POINT AT WINDOW 👇", "#00ff88"),
    ("\"Before you ask — yes, that’s an alien gunship firing plasma outside my window next to a Mustang…\"", "#00f0ff"),
    ("\"...and yes, our AI agents built my studio background too.\"", "#ffffff"),
    ("\"But what’s happening behind me is nothing compared to what we just deployed at Aria Technology Group.\"", "#00f0ff"),
    ("\"We rolled out our new Agentic Video Waiver software to brand-new employees with ZERO training.\"", "#d8b4fe"),
    ("\"No manuals. No onboarding sessions.\"", "#ffffff"),
    ("\"Instead of a rigid legacy screen, it runs a generative, iterative UI managed entirely by autonomous agents.\"", "#00f0ff"),
    ("\"When an employee hit friction or an edge case popped up, the software didn't crash —\"", "#ffffff"),
    ("\"— it self-healed and adapted the interface in real time. It was amazing.\"", "#d8b4fe"),
    ("\"At Aria Technology Group, we’re open-sourcing a massive part of this engine through Ariawave.\"", "#00f0ff"),
    ("\"But here’s the reality every leader needs to know: open-source code is not a production outcome.\"", "#facc15"),
    ("\"Running self-healing software in the real world takes layers of frontier intelligence, enterprise security, and true professionals.\"", "#00f0ff"),
    ("\"That’s why a specialized partner like Aria Technology Group makes all the difference.\"", "#ffffff"),
    ("\"If you want your operations running at light speed — reach out, and let's build.\"", "#00ff88"),
]

FULL_SCROLL_TEXT = """


[POINT OVER SHOULDER AT ALIEN SHIP & MUSTANG]
"Before you ask — yes, that’s an alien gunship
firing plasma outside my window next to a Mustang…
and yes, our AI agents built my studio background too."


[LEAN IN — CONVERSATIONAL]
"But what’s happening behind me is nothing compared
to what we just deployed at Aria Technology Group."


[THE VIDEO WAIVER STORY]
"We rolled out our new Agentic Video Waiver software
to brand-new employees with ZERO training.
No manuals. No onboarding sessions."


"Instead of a rigid legacy screen, the system runs a
generative, iterative UI managed by autonomous agents.
When an employee hit an edge case, it didn't crash —
it self-healed and adapted the interface in real time.
It was amazing."


[OPEN SOURCE VIA ARIAWAVE]
"At Aria Technology Group, we’re open-sourcing a
massive part of this engine through Ariawave."


[WHY CONSULTANTS MATTER]
"But open-source code is not a production outcome.
This takes layers of frontier intelligence, enterprise
security guardrails, and seasoned professionals."


[CALL TO ACTION]
"That’s why a partner like Aria Technology Group
makes all the difference. Reach out — and let's build."







"""

class TeleprompterHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ARIA STUDIO HUD // EYE-LINE TELEPROMPTER")
        self.root.configure(bg="#060911")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.94)

        # Position at top center of 1920x1080 screen (right under webcam!)
        w, h = 1180, 340
        sw = self.root.winfo_screenwidth()
        x = (sw - w) // 2
        self.root.geometry(f"{w}x{h}+{x}+0")

        # Top control bar
        top = tk.Frame(self.root, bg="#0f172a", height=48)
        top.pack(fill=tk.X, side=tk.TOP)

        self.status_lbl = tk.Label(
            top,
            text="● OBS READY (STANDBY) — CLICK 'START 5s COUNTDOWN & RECORD' OR PRESS SPACE",
            fg="#00f0ff",
            bg="#0f172a",
            font=("Segoe UI", 12, "bold"),
            padx=14,
            pady=8
        )
        self.status_lbl.pack(side=tk.LEFT)

        self.rec_btn = tk.Button(
            top,
            text="🔴 START 5s COUNTDOWN & RECORD IN OBS",
            bg="#ef4444",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padx=14,
            pady=4,
            command=self.trigger_record_or_stop
        )
        self.rec_btn.pack(side=tk.RIGHT, padx=10, pady=6)

        self.faster_btn = tk.Button(top, text="Speed +", bg="#1e293b", fg="#fff", command=lambda: self.adj_speed(0.3))
        self.faster_btn.pack(side=tk.RIGHT, padx=4)
        self.slower_btn = tk.Button(top, text="Speed -", bg="#1e293b", fg="#fff", command=lambda: self.adj_speed(-0.3))
        self.slower_btn.pack(side=tk.RIGHT, padx=4)

        # Canvas for smooth pixel scrolling
        self.canvas = tk.Canvas(self.root, bg="#060911", highlightthickness=2, highlightbackground="#00f0ff")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Eye-line guide markers on left/right
        self.canvas.create_line(0, 115, 1180, 115, fill="#00f0ff", dash=(6, 4), width=1)
        self.canvas.create_text(70, 98, text="👁️ EYE LINE", fill="#00f0ff", font=("Segoe UI", 10, "bold"))

        self.text_id = self.canvas.create_text(
            590,
            130,
            text=FULL_SCROLL_TEXT.strip(),
            fill="#f8fafc",
            font=("Segoe UI", 25, "bold"),
            width=1040,
            justify=tk.CENTER,
            anchor="n"
        )

        self.scrolling = False
        self.recording = False
        self.speed = 1.05  # pixels per frame (~32px/sec at 30fps)
        self.y_pos = 130.0

        self.root.bind("<space>", lambda e: self.trigger_record_or_stop())
        # Auto-start countdown in 2 seconds so user doesn't even have to click if standing!
        self.root.after(1500, self.start_countdown)
        self.animate()

    def adj_speed(self, delta):
        self.speed = max(0.3, min(3.5, self.speed + delta))

    def trigger_record_or_stop(self):
        if not self.recording:
            self.start_countdown()
        else:
            self.stop_obs_recording()

    def start_countdown(self):
        if self.recording:
            return
        self.recording = True
        self.rec_btn.configure(text="⏹ STOP RECORDING (SPACE)", bg="#f59e0b")
        self._countdown_step(5)

    def _countdown_step(self, sec):
        if not self.recording:
            return
        if sec > 0:
            self.status_lbl.configure(text=f"⏱️ STARTING OBS RECORDING IN {sec}... LOOK AT TOP OF SCREEN!", fg="#facc15")
            self.root.after(1000, lambda: self._countdown_step(sec - 1))
        else:
            self.status_lbl.configure(text="🔴 LIVE RECORDING IN OBS — SPEAK NATURALLY!", fg="#ff4444")
            self.scrolling = True
            threading.Thread(target=self._obs_start_rec_thread, daemon=True).start()

    def _obs_start_rec_thread(self):
        async def _go():
            try:
                async with websockets.connect("ws://127.0.0.1:4455") as ws:
                    await ws.recv()
                    await ws.send(json.dumps({"op": 1, "d": {"rpcVersion": 1}}))
                    await ws.recv()
                    await ws.send(json.dumps({"op": 6, "d": {"requestType": "StartRecord", "requestId": "rec_start"}}))
                    await ws.recv()
            except Exception as e:
                print("StartRecord err:", e)
        asyncio.run(_go())

    def stop_obs_recording(self):
        self.scrolling = False
        self.recording = False
        self.status_lbl.configure(text="✅ RECORDING SAVED! Tell Antigravity in chat or click again to re-shoot.", fg="#00ff88")
        self.rec_btn.configure(text="🔴 RE-SHOOT (START 5s COUNTDOWN)", bg="#ef4444")
        self.y_pos = 130.0
        self.canvas.coords(self.text_id, 590, self.y_pos)
        threading.Thread(target=self._obs_stop_rec_thread, daemon=True).start()

    def _obs_stop_rec_thread(self):
        async def _stop():
            try:
                async with websockets.connect("ws://127.0.0.1:4455") as ws:
                    await ws.recv()
                    await ws.send(json.dumps({"op": 1, "d": {"rpcVersion": 1}}))
                    await ws.recv()
                    await ws.send(json.dumps({"op": 6, "d": {"requestType": "StopRecord", "requestId": "rec_stop"}}))
                    while True:
                        msg = json.loads(await ws.recv())
                        if msg.get("op") == 7 and msg["d"].get("requestId") == "rec_stop":
                            out_path = msg["d"].get("responseData", {}).get("outputPath", "")
                            with open(r"C:\Users\Aria\.gemini\antigravity\scratch\last_obs_recording.txt", "w") as f:
                                f.write(out_path)
                            break
            except Exception as e:
                print("StopRecord err:", e)
        asyncio.run(_stop())

    def animate(self):
        if self.scrolling:
            self.y_pos -= self.speed
            self.canvas.coords(self.text_id, 590, self.y_pos)
        self.root.after(30, self.animate)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    TeleprompterHUD().run()
