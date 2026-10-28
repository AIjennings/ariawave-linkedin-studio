---
name: ariawave-linkedin-studio
description: >-
  Use this skill to shoot, teleprompter, edit, composite, clean dual-mic audio, caption, upscale, and publish
  executive LinkedIn / social videos on an Ariawave rig: OBS WebSocket v5 live framing, Always-On-Top Eye-Line
  Teleprompter HUD, L-R stereo pre-echo cancellation (Insta360 X5 + USB backup mic), O(1) Guided Filter natural
  face/ear matting over Veo/Cyberpunk video loops, dynamic word-highlighted ASS captions, and browser publishing
  via the Kimi WebBridge daemon (127.0.0.1:10086).
---

# Ariawave LinkedIn & Executive Video Studio (`ariawave-linkedin-studio`)

End-to-end autonomous broadcast studio pipeline for shooting, compositing, mastering, and publishing executive LinkedIn videos directly from an Ariawave rig (`DESKTOP-LL6P4P3` / `DESKTOP-SSO12SD`).

---

## 1. Live OBS Framing & Virtual Set Staging (`ws://127.0.0.1:4455`)

1. **Disable Static Cockpit Mask for Standing Shots:**
   - When shooting a standing/executive video with `Video Capture Device` (`Insta360 X5`), disable `Cockpit Cutout Mask` via OBS WebSocket `SetSourceFilterEnabled` (`filterEnabled: false`).
2. **Unlock & Center Camera Transform:**
   - Unlock scene items (`SetSceneItemLocked` -> `false`) and center the speaker (`scaleX/Y: 2.05`, `positionX: -665`, `positionY: -580`, `cropRight: 420`, `cropBottom: 150`).
3. **Start Virtual Camera (Optional for Zoom/Teams):**
   - Call `StartVirtualCam` over OBS WebSocket v5 (`ws://127.0.0.1:4455`).

---

## 2. Interactive Eye-Line Teleprompter HUD (Session 1 GUI Launch)

Because agent shells run in Session 0 or non-interactive contexts, launch GUI teleprompters in the user's active desktop session (`Session 1`) via the Ariawave Gaming OS server (`http://127.0.0.1:7777/api/gemini` with `{"action": "shell", "command": "..."}`):

- **Script:** `C:\Users\Aria\Desktop\obs_teleprompter_hud.py` (Tkinter borderless topmost overlay docked at `Y=0` right beneath the physical camera lens).
- **Controls:**
  - `SPACE` = Start 3-2-1 Countdown + Trigger OBS Recording (`StartRecord`) + Auto-Scroll
  - `UP` / `DOWN` = Adjust scroll speed (`0.5x` – `3.0x`)
  - `R` = Reset to top
  - `S` = Stop OBS Recording (`StopRecord`)

---

## 3. Dual-Mic Pre-Echo Cancellation (`L - R` Stereo Difference)

### The Hardware Phenomenon
When OBS records with both `Studio Mic (Default)` (`Insta360 X5`) and `USB Mic Backup` (`Headset Microphone`) unmuted:
- The **Insta360 X5** buffers its audio by **~195.4ms (`9381 samples` @ 48 kHz)** to match its internal 360° video stitching pipeline.
- The **USB Backup Mic** has zero latency (`0ms`) and is recorded as a **mono** signal (identical amplitude and phase on `L` and `R` channels), arriving **195.4ms ahead** of the main voice as a hollow/watery pre-echo.
- The **Insta360 X5** uses opposing stereo capsules (`L` and `R` have opposite polarity / stereo separation on the primary voice).

### The Exact Fix (Zero FFT Wateriness)
- **Never apply heavy `afftdn` or spectral STFT gating** to speech—it creates watery musical-noise phase artifacts.
- Instead, compute the stereo difference channel:
  ```python
  clean_mono = (left_channel - right_channel) * 0.80
  ```
- Because the USB backup mic is identical on `L` and `R`, `L - R` mathematically cancels the 195.4ms pre-echo down to the noise floor while preserving 100% dry, phase-coherent single-mic audio from the Insta360 X5.
- Follow with pure analog-style parametric EQ (`highpass=f=85`, `equalizer=f=3200:g=2.0`, `acompressor`, `loudnorm=I=-15:TP=-1.5:LRA=9`).

---

## 4. Natural Guided-Filter Matting (Zero Face or Ear Distortion)

### What to Avoid
- **Never use `cv2.erode` + rim-darkening** on MediaPipe Selfie Segmentation masks—it pinches inward on the speaker's ears and jawline.
- **Never apply `cv2.bilateralFilter`** across the speaker's face—it creates a plastic/warped skin appearance.

### The O(1) Guided Filter Pipeline
1. Run `mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)` and EMA-smooth temporally (`0.80 * cur + 0.20 * prev`).
2. Construct a chromaticity-boosted guide image `guide = clip(gray + (R - B) * 0.8, 0, 1)` so warm skin tones (face, ears, neck) have strong contrast against neutral grey studio walls.
3. Refine the alpha matte with an O(1) **Guided Filter** (`r=10, eps=5e-4`) and composite **100% untouched, natural camera pixels** (`fg_crop`) over the animated background loop.

---

## 5. Kimi WebBridge Browser Automation (`127.0.0.1:10086`)

To automate the user's logged-in desktop Microsoft Edge browser (LinkedIn publishing, Google Flow, etc.):
1. Ensure `C:\Users\Aria\.gemini\antigravity\scratch\kimi_webbridge_daemon.py` is running on `http://127.0.0.1:10086`.
2. The Kimi browser extension (`v2.0.24`) automatically connects to `ws://127.0.0.1:10086/ws`.
3. Send tool calls via HTTP `POST http://127.0.0.1:10086/command` with actions:
   - `list_browser_tabs`, `attach_tab`, `activate_tab`, `navigate`, `snapshot`, `read_page`, `click`, `fill`, `upload` (`files: ["C:\\path\\to\\video.mp4"]`), `evaluate`, `screenshot`.
