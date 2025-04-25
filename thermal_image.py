# thermal_image.py

import numpy as np
import cv2
import mlx90640

def capture_and_save(
    i2c_addr: int = 0x33,
    emissivity: float = 1.0,
    tr: float = 25.0,
    out_file: str = "thermal.jpg",
    scale_width: int = 320,
    scale_height: int = 240,
    min_temp: float = 20.0,
    max_temp: float = 35.0,
):
    """
    Capture two chess-mode frames to get all pixels, compute temperatures,
    apply a fixed temp window colormap, and upscale sharply.
    """
    # 1) EEPROM → numpy
    ee = mlx90640.dump_eeprom(i2c_addr)

    # 2) Calibration params
    params = mlx90640.Params()
    err = mlx90640.extract_parameters(ee, params)
    if err != 0:
        raise RuntimeError(f"Param extraction failed: {err}")

    # 3) Read two frames & combine subpages
    #    Pre-allocate the temperature result buffer:
    to_data = np.zeros(768, dtype=np.float32)
    for _ in range(2):
        frame = mlx90640.get_frame_data(i2c_addr)
        mlx90640.calculate_to(frame, params, emissivity, tr, to_data)

    # 4) Reshape 1D→2D
    img = to_data.reshape((24, 32))

    # 5) Fixed-range normalization
    norm = (img - min_temp) / (max_temp - min_temp)
    norm8 = np.clip(norm * 255.0, 0, 255).astype(np.uint8)

    # 6) Colormap
    colored = cv2.applyColorMap(norm8, cv2.COLORMAP_JET)

    # 7) Nearest-neighbor upscale for crisp blocks
    colored = cv2.resize(
        colored,
        (scale_width, scale_height),
        interpolation=cv2.INTER_NEAREST
    )

    # 8) Save JPEG
    if not cv2.imwrite(out_file, colored):
        raise RuntimeError(f"Failed to write {out_file}")
    print(f"Saved {out_file} (mapped {min_temp:.1f}–{max_temp:.1f}°C)")

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(
        description="Capture MLX90640 chess frames and save a thermal .jpg"
    )
    p.add_argument("--addr",     type=lambda x: int(x,0), default=0x33)
    p.add_argument("--emissivity", type=float, default=1.0)
    p.add_argument("--tr",       type=float, default=25.0,
                   help="Reflected ambient temp (°C)")
    p.add_argument("--output",   default="thermal.jpg")
    p.add_argument("--width",    type=int, default=320)
    p.add_argument("--height",   type=int, default=240)
    p.add_argument("--min-temp", type=float, default=20.0)
    p.add_argument("--max-temp", type=float, default=35.0)

    args = p.parse_args()
    capture_and_save(
        i2c_addr=args.addr,
        emissivity=args.emissivity,
        tr=args.tr,
        out_file=args.output,
        scale_width=args.width,
        scale_height=args.height,
        min_temp=args.min_temp,
        max_temp=args.max_temp,
    )
