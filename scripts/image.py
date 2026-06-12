# scripts/make_carrier.py

from PIL import Image
import numpy as np

# Simulate a natural photo with gaussian noise
np.random.seed(42)
base = np.random.normal(loc=128, scale=45, size=(512, 512, 3))
base = np.clip(base, 0, 255).astype(np.uint8)


for i in range(512):
    for j in range(512):
        base[i,j,0] = min(255, int(base[i,j,0] * (0.8 + 0.4*(i/512))))
        base[i,j,2] = min(255, int(base[i,j,2] * (0.8 + 0.4*(j/512))))

img = Image.fromarray(base, 'RGB')
img.save("images/carrier.png")
print("Realistic carrier created")