from stegano import lsb
from PIL import Image
import piexif, os, base64

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "../images")

def lsb_decode(path):
    try:
        msg = lsb.reveal(path)
        return msg
    except Exception as e:
        return None

def exif_decode(path):
    try:
        exif = piexif.load(path)
        raw = exif["Exif"].get(piexif.ExifIFD.UserComment, b"")
        return raw.decode(errors="ignore") if raw else None
    except:
        return None

def try_deobfuscate(text):
    """Try Base64 decode — catches obfuscated payloads"""
    try:
        return base64.b64decode(text).decode()
    except:
        return None

if __name__ == "__main__":
    test_images = [
        "carrier.png",
        "stego_lsb_subtle.png",
        "stego_lsb_direct.png",
        "stego_lsb_obfuscated.png",
        "stego_exif_subtle.png",
    ]

    for name in test_images:
        path = os.path.join(IMAGES_DIR, name)
        if not os.path.exists(path):
            continue
        lsb_msg  = lsb_decode(path)
        exif_msg = exif_decode(path)
        deob     = try_deobfuscate(lsb_msg) if lsb_msg else None

        print(f"\n--- {name} ---")
        print(f"  LSB  : {lsb_msg}")
        print(f"  EXIF : {exif_msg}")
        if deob:
            print(f"  DEOB : {deob}")