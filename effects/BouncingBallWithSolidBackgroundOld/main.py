import sys
import os
import time
import json
import signal
import ctypes
import random
import cfg_helper
import appserver

from rich import print
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType

# ======================================================
#  VISUALIZER IMPORT
# ======================================================
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Visualizer"))
from visualizer import Visualizer

vis = Visualizer()

# ======================================================
#  CLEAN SERVICE STOP HANDLING
# ======================================================

stop_flag = False

def handle_stop(signum, frame):
    global stop_flag
    stop_flag = True
    try:
        vis._force_stop_server()
    except Exception:
        pass

signal.signal(signal.SIGTERM, handle_stop)
signal.signal(signal.SIGINT, handle_stop)

# ======================================================
#  LOAD CONFIG.JSON
# ======================================================




# ======================================================
#  GO SHARED LIBRARY BINDINGS
# ======================================================

LIB_PATH = os.path.join(os.path.dirname(__file__), "gophysics", "libadvbounce.so")
lib = ctypes.CDLL(LIB_PATH)

class EffectConfig(ctypes.Structure):
    _fields_ = [
        # core physics
        ("gravity", ctypes.c_double),
        ("bounciness_vertical", ctypes.c_double),
        ("bounciness_horizontal", ctypes.c_double),
        ("max_speed", ctypes.c_double),
        ("fps", ctypes.c_double),

        # initial velocity
        ("initial_vx", ctypes.c_double),
        ("initial_vy", ctypes.c_double),

        # air drag (dt-based)
        ("enable_air_drag_x", ctypes.c_int),
        ("enable_air_drag_y", ctypes.c_int),
        ("air_drag_x_rate", ctypes.c_double),
        ("air_drag_y_rate", ctypes.c_double),
        ("air_drag_x_min_speed", ctypes.c_double),
        ("air_drag_y_min_speed", ctypes.c_double),

        # spin torque
        ("enable_spin_torque", ctypes.c_int),
        ("spin_torque_strength", ctypes.c_double),

        # squish
        ("squish_enabled", ctypes.c_int),
        ("squish_decay_rate", ctypes.c_double),
        ("squish_factor", ctypes.c_double),
        ("squish_max", ctypes.c_double),

        # random impulse
        ("enable_random_impulse_x", ctypes.c_int),
        ("enable_random_impulse_y", ctypes.c_int),
        ("rand_impulse_x_min", ctypes.c_double),
        ("rand_impulse_x_max", ctypes.c_double),
        ("rand_impulse_y_min", ctypes.c_double),
        ("rand_impulse_y_max", ctypes.c_double),
        ("rand_impulse_x_max_speed", ctypes.c_double),
        ("rand_impulse_y_max_speed", ctypes.c_double),

        # bounce flicker
        ("enable_bounce_flicker", ctypes.c_int),
        ("flicker_decay_rate", ctypes.c_double),

        # impact squash
        ("enable_impact_squash", ctypes.c_int),
        ("impact_squash_mult", ctypes.c_double),
        ("impact_recovery_rate", ctypes.c_double),

        # squish tilt
        ("enable_squish_tilt", ctypes.c_int),
        ("tilt_factor", ctypes.c_double),

        # magnetic squish
        ("enable_magnetic_squish", ctypes.c_int),
        ("magnetic_range", ctypes.c_double),
        ("magnetic_strength", ctypes.c_double),

        # jiggle
        ("enable_jiggle", ctypes.c_int),
        ("jiggle_strength", ctypes.c_double),
        ("jiggle_freq", ctypes.c_double),
        ("jiggle_decay_rate", ctypes.c_double),

        # stuck / unsticking
        ("stuck_y_tolerance", ctypes.c_double),
        ("stuck_threshold_time", ctypes.c_double),
        ("stuck_impulse_min", ctypes.c_double),
        ("stuck_impulse_max", ctypes.c_double),

        # radii
        ("ball_radius", ctypes.c_double),
        ("halo_radius", ctypes.c_double),

        # trail
        ("enable_trail_effect", ctypes.c_int),
        ("trail_new_color_percent", ctypes.c_double),

        # color modes
        ("enable_rainbow_ball", ctypes.c_int),
        ("enable_heatmap_glow", ctypes.c_int),

        # colors
        ("ball_r", ctypes.c_uint8),
        ("ball_g", ctypes.c_uint8),
        ("ball_b", ctypes.c_uint8),
        ("bg_r", ctypes.c_uint8),
        ("bg_g", ctypes.c_uint8),
        ("bg_b", ctypes.c_uint8),
    ]

lib.InitEffect.argtypes = [ctypes.POINTER(EffectConfig), ctypes.c_int]
lib.InitEffect.restype = None

lib.StepEffect.argtypes = [ctypes.c_double, ctypes.c_double]
lib.StepEffect.restype = None

lib.GetFrame.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # positions
    ctypes.POINTER(ctypes.c_ubyte),   # colors
]
lib.GetFrame.restype = None

# ======================================================
#  OPENRGB SETUP
# ======================================================

client = OpenRGBClient(name="AdvGravityBounce-Go")
kb = client.get_devices_by_type(DeviceType.KEYBOARD)[0]
led_count = len(kb.leds)

kb.set_colors([RGBColor(0, 0, 0)] * led_count)
time.sleep(0.5)

# ======================================================
#  PREPARE GO CONFIG FROM JSON
# ======================================================

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_PATH, "r") as f:
    json_cfg = json.load(f)

def parse_rgb(name: str):
    v = json_cfg[name]
    if isinstance(v, list) and len(v) == 4 and v[0] == "RGBColor":
        return int(v[1]), int(v[2]), int(v[3])
    raise ValueError(f"Config field {name} must be ['RGBColor', r, g, b]")

cfg = EffectConfig()

ball_r, ball_g, ball_b = parse_rgb("BALL_COLOR")
bg_r, bg_g, bg_b = parse_rgb("BACKGROUND_COLOR")

cfg.gravity = json_cfg["GRAVITY"]
cfg.bounciness_vertical = json_cfg["BOUNCINESS_VERTICAL"]
cfg.bounciness_horizontal = json_cfg["BOUNCINESS_HORIZONTAL"]
cfg.max_speed = json_cfg["MAX_SPEED"]
cfg.fps = json_cfg["FPS"]

# initial velocities
cfg.initial_vx = json_cfg["SPEED_X"] * (1 if random.random() < 0.5 else -1)
cfg.initial_vy = -json_cfg["INITIAL_VY"]

# air drag
cfg.enable_air_drag_x = int(json_cfg["ENABLE_AIR_DRAG_X"])
cfg.enable_air_drag_y = int(json_cfg["ENABLE_AIR_DRAG_Y"])
cfg.air_drag_x_rate = json_cfg["AIR_DRAG_X_RATE"]
cfg.air_drag_y_rate = json_cfg["AIR_DRAG_Y_RATE"]
cfg.air_drag_x_min_speed = json_cfg["AIR_DRAG_X_MIN_SPEED"]
cfg.air_drag_y_min_speed = json_cfg["AIR_DRAG_Y_MIN_SPEED"]

# spin torque
cfg.enable_spin_torque = int(json_cfg["ENABLE_SPIN_TORQUE"])
cfg.spin_torque_strength = json_cfg["SPIN_TORQUE_STRENGTH"]

# squish
cfg.squish_enabled = int(json_cfg["SQUISH_ENABLED"])
cfg.squish_decay_rate = json_cfg["SQUISH_DECAY_RATE"]
cfg.squish_factor = json_cfg["SQUISH_FACTOR"]
cfg.squish_max = json_cfg["SQUISH_MAX"]

# random impulse
cfg.enable_random_impulse_x = int(json_cfg["ENABLE_RANDOM_IMPULSE_X"])
cfg.enable_random_impulse_y = int(json_cfg["ENABLE_RANDOM_IMPULSE_Y"])
cfg.rand_impulse_x_min = json_cfg["RANDOM_IMPULSE_X_MIN"]
cfg.rand_impulse_x_max = json_cfg["RANDOM_IMPULSE_X_MAX"]
cfg.rand_impulse_y_min = json_cfg["RANDOM_IMPULSE_Y_MIN"]
cfg.rand_impulse_y_max = json_cfg["RANDOM_IMPULSE_Y_MAX"]
cfg.rand_impulse_x_max_speed = json_cfg["RANDOM_IMPULSE_X_MAX_SPEED"]
cfg.rand_impulse_y_max_speed = json_cfg["RANDOM_IMPULSE_Y_MAX_SPEED"]

# bounce flicker
cfg.enable_bounce_flicker = int(json_cfg["ENABLE_BOUNCE_FLICKER"])
cfg.flicker_decay_rate = json_cfg["FLICKER_DECAY_RATE"]

# impact squash
cfg.enable_impact_squash = int(json_cfg["ENABLE_IMPACT_SQUASH"])
cfg.impact_squash_mult = json_cfg["IMPACT_SQUASH_MULT"]
cfg.impact_recovery_rate = json_cfg["IMPACT_RECOVERY_RATE"]

# squish tilt
cfg.enable_squish_tilt = int(json_cfg["ENABLE_SQUISH_TILT"])
cfg.tilt_factor = json_cfg["TILT_FACTOR"]

# magnetic squish
cfg.enable_magnetic_squish = int(json_cfg["ENABLE_MAGNETIC_SQUISH"])
cfg.magnetic_range = json_cfg["MAGNETIC_RANGE"]
cfg.magnetic_strength = json_cfg["MAGNETIC_STRENGTH"]

# jiggle
cfg.enable_jiggle = int(json_cfg["ENABLE_JIGGLE"])
cfg.jiggle_strength = json_cfg["JIGGLE_STRENGTH"]
cfg.jiggle_freq = json_cfg["JIGGLE_FREQ"]
cfg.jiggle_decay_rate = json_cfg["JIGGLE_DECAY_RATE"]

# stuck / unsticking
cfg.stuck_y_tolerance = json_cfg["STUCK_Y_TOLERANCE"]
cfg.stuck_threshold_time = json_cfg["STUCK_THRESHOLD_TIME"]
cfg.stuck_impulse_min = json_cfg["STUCK_IMPULSE_MIN"]
cfg.stuck_impulse_max = json_cfg["STUCK_IMPULSE_MAX"]

# radii
cfg.ball_radius = json_cfg["BALL_RADIUS"]
cfg.halo_radius = json_cfg["HALO_RADIUS"]

# trail
cfg.enable_trail_effect = int(json_cfg["ENABLE_TRAIL_EFFECT"])
cfg.trail_new_color_percent = json_cfg["TRAIL_NEW_COLOR_PERCENT"]

# color modes
cfg.enable_rainbow_ball = int(json_cfg["ENABLE_RAINBOW_BALL"])
cfg.enable_heatmap_glow = int(json_cfg["ENABLE_HEATMAP_GLOW"])

# base colors
cfg.ball_r = ball_r
cfg.ball_g = ball_g
cfg.ball_b = ball_b

cfg.bg_r = bg_r
cfg.bg_g = bg_g
cfg.bg_b = bg_b

# ======================================================
#  INIT EFFECT IN GO
# ======================================================

lib.InitEffect(ctypes.byref(cfg), led_count)

# Preallocate buffers for positions + colors
pos_buf = (ctypes.c_double * (led_count * 2))()
col_buf = (ctypes.c_ubyte * (led_count * 3))()

# ======================================================
#  MAIN LOOP
# ======================================================

def main():
    global stop_flag

    frame_dt = 1.0 / json_cfg["FPS"]
    last = time.monotonic()
    fresh = True

    print("[green]Advanced Gravity Bouncing Ball (Go engine) running...[/green]")

    while not stop_flag:
        now = time.monotonic()
        dt = now - last
        last = now
        if dt <= 0:
            dt = frame_dt

        # Step physics in Go
        lib.StepEffect(ctypes.c_double(dt), ctypes.c_double(now))

        # Fetch frame (positions + colors)
        lib.GetFrame(pos_buf, col_buf)

        # Positions for visualizer
        positions = [
            (pos_buf[i * 2], pos_buf[i * 2 + 1])
            for i in range(led_count)
        ]

        # Colors back into RGBColor for OpenRGB + visualizer
        safe_colors = []
        for i in range(led_count):
            r = col_buf[i * 3]
            g = col_buf[i * 3 + 1]
            b = col_buf[i * 3 + 2]
            safe_colors.append(RGBColor(int(r), int(g), int(b)))

        # Push to OpenRGB
        kb.set_colors(safe_colors)

        # Update visualizer
        vis.update(positions, safe_colors)

        if fresh:
            time.sleep(2.0)
            fresh = False
            last = time.monotonic()
            continue

        # Frame pacing
        sleep_time = frame_dt - (time.monotonic() - now)
        if sleep_time > 0:
            print(sleep_time)
            time.sleep(sleep_time)

    sys.exit(0)


if __name__ == "__main__":
    main()