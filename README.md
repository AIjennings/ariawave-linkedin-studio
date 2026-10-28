# Ariawave LinkedIn Studio // Autonomous Executive Video Pipeline

**Built by [Aria Technology Group](https://www.ariawave.tech)**  
*Frontier Agentic AI • Self-Healing Enterprise UI • Open-Source Sovereign Media Tooling*

![Preview Frame](assets/preview_frame_v3.jpg)

---

## Overview

This repository contains the end-to-end **Ariawave LinkedIn Broadcast & Post-Production Pipeline** produced by Aria Technology Group's autonomous agent stack:

1. **Live OBS Studio WebSocket v5 Framing & Teleprompter HUD (`teleprompter/obs_teleprompter_hud.py`)**
   - Connects directly to OBS Studio (`ws://127.0.0.1:4455`), unlocks and centers the Insta360 X5 studio camera, and docks an always-on-top eye-line teleprompter HUD at `Y=0` directly below the camera lens.
   - Single-key (`SPACE`) 3-2-1 countdown that triggers `StartRecord` in OBS and scrolls the script in sync with the speaker.

2. **Dual-Mic Pre-Echo Cancellation (`scripts/build_linkedin_v3_clean.py`)**
   - Solves the `195.4ms` pre-echo caused when OBS records both an **Insta360 X5** (`195.4ms` internal stitching delay) and a zero-latency mono **USB Backup Mic** onto Track 1.
   - Uses stereo difference `(L - R) * 0.80` to mathematically cancel the mono USB backup mic down to the room noise floor while keeping the primary voice 100% dry, phase-coherent, and free of FFT spectral-denoise wateriness.

3. **Natural O(1) Guided Filter Matting (`scripts/build_linkedin_v3_clean.py`)**
   - Pairs MediaPipe Selfie Segmentation (`model_selection=1`) with an O(1) **Guided Filter** guided by skin/hair chromaticity (`gray + 0.8 * (R - B)`).
   - Preserves **100% natural, untouched camera pixels** across the speaker's face, ears, hair, and shirt (zero morphological ear pinching or bilateral plastic blurring) while compositing over the animated **Mustang S550 + Alien Gunship Cyberpunk Penthouse** loop.

4. **Dynamic Word-Highlighted Subtitles & 2K Mastering (`subtitles/linkedin_captions.ass`)**
   - Burned-in executive lower-third captions (`Segoe UI Bold`) with cyan/gold keyword emphasis and top-left `ARIA TECHNOLOGY GROUP // ARIAWAVE.TECH` badge.
   - Outputs both `1080p` (`1920x1080` @ 30fps) and `2K QHD` (`2560x1440` Lanczos + Unsharp mask) masters.

5. **Kimi WebBridge Local Agent Server (`scripts/kimi_webbridge_daemon.py`)**
   - Local WebSocket + HTTP bridge (`127.0.0.1:10086`) enabling autonomous browser agents to drive the logged-in desktop Microsoft Edge browser via the Kimi extension (`v2.0.24`).

---

## Repository Structure

```text
ariawave-linkedin-studio/
├── assets/
│   └── preview_frame_v3.jpg             # Verified v3 composite frame (natural matting + captions)
├── scripts/
│   ├── build_linkedin_v3_clean.py       # Full v3 audio cancellation, guided matting, ASS burn-in & 2K upscale
│   └── kimi_webbridge_daemon.py         # Local WebBridge daemon (ws://127.0.0.1:10086/ws + POST /command)
├── skills/
│   └── ariawave-linkedin-studio/
│       └── SKILL.md                     # Agent skill definition for Ariawave rigs
├── subtitles/
│   └── linkedin_captions.ass            # Timed ASS subtitle & header overlay definitions
└── teleprompter/
    ├── Aria_LinkedIn_Teleprompter.html  # Standalone browser teleprompter + script copy
    └── obs_teleprompter_hud.py          # Always-on-top Tkinter eye-line teleprompter synced with OBS WebSocket
```

---

## About Aria Technology Group

**Aria Technology Group** (`ariawave.tech`) designs and deploys **Self-Healing Generative Enterprise UI** and **Frontier Multi-Agent Systems**—including the **Agentic Video Waiver** platform that enables brand-new employees to operate complex workflows with zero training. While we open-source core building blocks through **Ariawave**, delivering production enterprise outcomes requires layers of frontier intelligence, strict security guardrails, and seasoned engineering leadership.
