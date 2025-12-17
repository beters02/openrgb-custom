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

cfghelper = cfg_helper.CFGHelper(EffectConfig(), lib)

# ======================================================
#  INIT EFFECT IN GO
# ======================================================

lib.InitEffect(ctypes.byref(cfghelper.cfg), led_count)

# Preallocate buffers for positions + colors
pos_buf = (ctypes.c_double * (led_count * 2))()
col_buf = (ctypes.c_ubyte * (led_count * 3))()

# ======================================================
#  MAIN LOOP
# ======================================================

def main():
    global stop_flag

    frame_dt = 1.0 / cfghelper.json_cfg["FPS"]
    last = time.monotonic()
    fresh = True

    print("[green]Advanced Gravity Bouncing Ball (Go engine) running...[/green]")

    while not stop_flag:
        

        now = time.monotonic()
        dt = now - last
        last = now
        if dt <= 0:
            dt = frame_dt

        #srv.update(cfghelper)
        cfghelper.update(dt)

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