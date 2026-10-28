#!/usr/bin/env python3
r"""
Build 3 high-impact LinkedIn BTS Video Assets from the 2 iPhone 4K videos:
1. ARIA_TECH_GROUP_BTS_Part1_OBS_Agents_1080x1920.mp4 (19.3s)
2. ARIA_TECH_GROUP_BTS_Part2_GarbageIn_GoldOut_1080x1920.mp4 (32.0s)
3. ARIA_TECH_GROUP_BTS_Combined_Supercut_1080x1920.mp4 (51.3s)
"""
import os
import subprocess

SCRATCH = r"C:\Users\Aria\.gemini\antigravity\scratch"
BTS_DIR = r"C:\Users\Aria\Desktop\BTS_Uploads"
DESKTOP = r"C:\Users\Aria\Desktop"

CLIP1_IN = os.path.join(BTS_DIR, "VID_20261028_130444_9622.mov")
CLIP2_IN = os.path.join(BTS_DIR, "VID_20261028_130650_9623.mov")

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,54,&H00FFFFFF,&H0000F0FF,&H00080C14,&HA0000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,60,60,210,1
Style: TopTag,Consolas,30,&H00FFE600,&H00FFFFFF,&H00080C14,&HC0080C14,-1,0,0,0,100,100,1.5,0,3,12,0,8,50,50,85,1
Style: SubTag,Segoe UI Semibold,24,&H00E2E8F0,&H00FFFFFF,&H00080C14,&H00000000,-1,0,0,0,100,100,1.0,0,1,2.5,1.0,8,50,50,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Cyan: {\c&HFFE600&}, Gold: {\c&H00D4FF&}, White: {\c&HFFFFFF&}
CLIP1_EVENTS = [
    ("0:00:00.00", "0:00:19.30", "TopTag", "ARIA TECHNOLOGY GROUP // BEHIND THE SCENES"),
    ("0:00:00.00", "0:00:19.30", "SubTag", "AUTONOMOUS OBS STUDIO • MULTI-AGENT STACK"),
    ("0:00:00.10", "0:00:05.30", "Default", r"I've got {\c&HFFE600&}AI agents{\c&HFFFFFF&} running my {\c&H00D4FF&}OBS Studio{\c&HFFFFFF&} live."),
    ("0:00:06.10", "0:00:11.30", "Default", r"This is the {\c&H00D4FF&}Behind The Scenes{\c&HFFFFFF&} from the video we just shot."),
    ("0:00:11.80", "0:00:16.20", "Default", r"{\c&HFFE600&}AI on top of AI{\c&HFFFFFF&} on top of AI — on top of {\c&H00D4FF&}virtual desktops{\c&HFFFFFF&}."),
    ("0:00:16.20", "0:00:19.30", "Default", r"This is what we do at {\c&HFFE600&}Aria Technology Group{\c&HFFFFFF&}."),
]

CLIP2_EVENTS = [
    ("0:00:00.00", "0:00:32.00", "TopTag", "ARIA TECHNOLOGY GROUP // GARBAGE IN -> GOLD OUT"),
    ("0:00:00.00", "0:00:32.00", "SubTag", "EYE-LINE TELEPROMPTER HUD • INSTA360 X5 • ZERO-CLICK EDIT"),
    ("0:00:00.10", "0:00:05.80", "Default", r"Just finished shooting with the {\c&HFFE600&}AI Teleprompter{\c&HFFFFFF&} & {\c&H00D4FF&}Insta360{\c&HFFFFFF&} virtual set."),
    ("0:00:05.80", "0:00:12.40", "Default", r"Now the agent is {\c&HFFE600&}editing{\c&HFFFFFF&} — cutting my {\c&H00D4FF&}awkward pause{\c&HFFFFFF&} at the start automatically."),
    ("0:00:12.80", "0:00:19.80", "Default", r"Look at how {\c&H00D4FF&}messy my raw prompts{\c&HFFFFFF&} are — typos and all."),
    ("0:00:20.30", "0:00:23.20", "Default", r"A {\c&HFFE600&}real agentic system{\c&HFFFFFF&} just handles it for you."),
    ("0:00:23.30", "0:00:28.50", "Default", r"Prompt perfection doesn't matter when your {\c&HFFE600&}agents self-heal{\c&HFFFFFF&}."),
    ("0:00:28.50", "0:00:32.00", "Default", r"Put {\c&H00D4FF&}messy input in{\c&HFFFFFF&} — get {\c&HFFE600&}production gold out{\c&HFFFFFF&}."),
]

def write_ass(path, events):
    with open(path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        for st, et, style, txt in events:
            f.write(f"Dialogue: 0,{st},{et},{style},,0,0,0,,{txt}\n")

ass1_path = os.path.join(SCRATCH, "bts_part1.ass")
ass2_path = os.path.join(SCRATCH, "bts_part2.ass")
write_ass(ass1_path, CLIP1_EVENTS)
write_ass(ass2_path, CLIP2_EVENTS)

def render_bts(in_mov, dur, ass_file, out_mp4):
    ass_esc = ass_file.replace("\\", "/").replace(":", "\\:")
    af = "highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-18dB:ratio=2.5:attack=10:release=120:makeup=2dB,loudnorm=I=-15:TP=-1.5:LRA=9"
    vf = f"scale=1080:1920:flags=lanczos,ass='{ass_esc}'"
    cmd = [
        "ffmpeg", "-y",
        "-i", in_mov,
        "-t", f"{dur:.2f}",
        "-vf", vf,
        "-af", af,
        "-r", "30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        out_mp4
    ]
    print("Rendering:", out_mp4)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

out1 = os.path.join(DESKTOP, "ARIA_TECH_GROUP_BTS_Part1_OBS_Agents_1080x1920.mp4")
out2 = os.path.join(DESKTOP, "ARIA_TECH_GROUP_BTS_Part2_GarbageIn_GoldOut_1080x1920.mp4")
out_combo = os.path.join(DESKTOP, "ARIA_TECH_GROUP_BTS_Combined_Supercut_1080x1920.mp4")

render_bts(CLIP1_IN, 19.30, ass1_path, out1)
render_bts(CLIP2_IN, 32.00, ass2_path, out2)

# Concatenate out1 + out2 into Combined Supercut
concat_txt = os.path.join(SCRATCH, "bts_concat.txt")
with open(concat_txt, "w", encoding="utf-8") as f:
    f.write(f"file '{out1.replace(chr(92), '/')}'\n")
    f.write(f"file '{out2.replace(chr(92), '/')}'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
    "-c", "copy", "-movflags", "+faststart", out_combo
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Extract verification frames from Part 1 and Part 2
subprocess.run(["ffmpeg", "-y", "-ss", "2.5", "-i", out1, "-frames:v", "1", "-q:v", "2", os.path.join(SCRATCH, "verify_bts1.jpg")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-y", "-ss", "15.0", "-i", out2, "-frames:v", "1", "-q:v", "2", os.path.join(SCRATCH, "verify_bts2.jpg")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("ALL 3 BTS MASTERS COMPLETED!")
