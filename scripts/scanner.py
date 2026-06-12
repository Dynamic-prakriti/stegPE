"""
Detection Robustness Scanner
Tests how reliably steganographic content can be detected
before it reaches the LLM, and whether sanitization removes it.
"""

from stegano import lsb
from PIL import Image
import piexif, os, json, hashlib, base64
from datetime import datetime
import numpy as np
import re

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "../images")
LOGS_DIR   = os.path.join(os.path.dirname(__file__), "../logs")

# ── Detection methods ──────────────────────────────────────────

def detect_lsb(path):
    try:
        msg = lsb.reveal(path)
        return {"detected": bool(msg), "payload": msg}
    except:
        return {"detected": False, "payload": None}

def detect_exif(path):
    # Method 1: PIL (works for PNG + JPEG)
    try:
        img = Image.open(path)
        raw = img.info.get("exif", b"")
        if raw:
            # Decode strip the Exif header prefix
            text = raw.decode("latin-1", errors="ignore")
            # Extract readable ASCII text from the binary blob
            import re
            readable = re.findall(r'[ -~]{4,}', text)
            payload = " ".join(readable).strip()
            # Filter out EXIF structural strings
            skip = {"Exif", "MM", "II", "ASCII"}
            cleaned = " ".join(
                p for p in readable
                if p not in skip and len(p) > 5
            ).strip()
            if cleaned:
                return {"detected": True, "payload": cleaned}
    except Exception as e:
        pass

    # Method 2: piexif fallback (JPEG/TIFF only)
    try:
        exif = piexif.load(path)
        raw = exif["Exif"].get(piexif.ExifIFD.UserComment, b"")
        if raw.startswith(b"ASCII\x00\x00\x00"):
            raw = raw[8:]
        msg = raw.decode("utf-8", errors="ignore").strip()
        if msg:
            return {"detected": True, "payload": msg}
    except:
        pass

    return {"detected": False, "payload": None}
    

def entropy_check(path):
    """
    Improved LSB entropy analysis.
    Compares LSB ratio against expected natural image baseline.
    Natural photos: ratio typically 0.45-0.55 but NOT tightly at 0.5
    Stego images: ratio converges very tightly toward exactly 0.5
    Uses standard deviation of per-channel ratios as additional signal.
    """
    img = Image.open(path).convert("RGB")
    pixels = np.array(img)

    r_lsb = pixels[:,:,0] & 1
    g_lsb = pixels[:,:,1] & 1
    b_lsb = pixels[:,:,2] & 1

    r_ratio = float(r_lsb.mean())
    g_ratio = float(g_lsb.mean())
    b_ratio = float(b_lsb.mean())
    overall = (r_ratio + g_ratio + b_ratio) / 3

   
    channel_std = float(np.std([r_ratio, g_ratio, b_ratio]))

   
    suspicious = (abs(overall - 0.5) < 0.01) and (channel_std < 0.01)

    return {
        "lsb_ones_ratio": round(overall, 4),
        "channel_std":    round(channel_std, 5),
        "r_ratio":        round(r_ratio, 4),
        "g_ratio":        round(g_ratio, 4),
        "b_ratio":        round(b_ratio, 4),
        "entropy_flag":   suspicious
    }

def sanitize(input_path, output_path):
    """
    Re-save via PIL — strips EXIF metadata.
    Does NOT remove LSB steganography (pixels are preserved).
    """
    img = Image.open(input_path)
    img.save(output_path)
    return output_path

def detect_obfuscation(payload):
    """Try Base64 decode — catches obfuscated payloads"""
    if not payload:
        return None
    try:
        import base64
        decoded = base64.b64decode(payload).decode("utf-8")
        # Only return if decoded result is readable ASCII
        if all(32 <= ord(c) <= 126 for c in decoded):
            return decoded
        return None
    except:
        return None
    
# ── Full scan pipeline ─────────────────────────────────────────


def full_scan(path):
    result = {
        "timestamp": datetime.now().isoformat(),
        "file": os.path.basename(path),
        "lsb":  detect_lsb(path)  if path.endswith(".png") else {"detected": False, "payload": None},
        "exif": detect_exif(path),
        "entropy": entropy_check(path),
        "deobfuscated": None,
        "sanitized_lsb_survives":  None,
        "sanitized_exif_survives": None,
    }

    lsb_payload = result["lsb"]["payload"]
    result["deobfuscated"] = detect_obfuscation(lsb_payload)

    sanitized_path = path.replace(".png", "_sanitized.png").replace(".jpg", "_sanitized.jpg")
    sanitize(path, sanitized_path)
    result["sanitized_lsb_survives"]  = detect_lsb(sanitized_path)["detected"]  if sanitized_path.endswith(".png") else False
    result["sanitized_exif_survives"] = detect_exif(sanitized_path)["detected"]

    return result

if __name__ == "__main__":
    test_images = [
        "carrier.png",
        "stego_lsb_subtle.png",
        "stego_lsb_direct.png",
        "stego_lsb_obfuscated.png",
        "stego_exif_subtle.png",
        "stego_exif_direct.png",
    ]

    report = []
    for name in test_images:
        path = os.path.join(IMAGES_DIR, name)
        if not os.path.exists(path):
            print(f"[skip] {name} not found")
            continue
        result = full_scan(path)
        report.append(result)

        print(f"\n=== {name} ===")
        print(f"  LSB detected     : {result['lsb']['detected']}")
        print(f"  EXIF detected    : {result['exif']['detected']}")
        print(f"  Entropy flag     : {result['entropy']['entropy_flag']} "
              f"(ratio={result['entropy']['lsb_ones_ratio']})")
        print(f"  Deobfuscated     : {result['deobfuscated']}")
        print(f"  After sanitize:")
        print(f"    LSB survives   : {result['sanitized_lsb_survives']}")
        print(f"    EXIF survives  : {result['sanitized_exif_survives']}")

    out = os.path.join(LOGS_DIR, "scanner_report.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[+] Report saved to {out}")