import os
import json
import random
import ctypes

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def do_parse_rgb(json, name: str):
    v = json[name]
    if isinstance(v, list) and len(v) == 4 and v[0] == "RGBColor":
        return int(v[1]), int(v[2]), int(v[3])
    raise ValueError(f"Config field {name} must be ['RGBColor', r, g, b]")

def debugPrint(msg):
    print(msg, flush=True)

class CFGHelper:
    def __init__(self, cfg, lib):
        self.cfg = cfg
        self.last_check_debounce = 0
        self.last_ball_r = 0
        self.last_ball_g = 0
        self.last_ball_b = 0
        self.last_bg_r = 0
        self.last_bg_g = 0
        self.last_bg_b = 0
        self.lib = lib
        self.parse_json()
        

    def parse_rgb(self, name: str):
        return do_parse_rgb(self.json_cfg, name)

    def parse_json(self):
        with open(CONFIG_PATH, "r") as f:
            self.json_cfg = json.load(f)
        ball_r, ball_g, ball_b = self.parse_rgb("BALL_COLOR")
        bg_r, bg_g, bg_b = self.parse_rgb("BACKGROUND_COLOR")

        self.last_ball_r = ball_r
        self.last_ball_g = ball_g
        self.last_ball_b = ball_b
        self.last_bg_r = bg_r
        self.last_bg_g = bg_g
        self.last_bg_b = bg_b

        self.cfg.gravity = self.json_cfg["GRAVITY"]
        self.cfg.bounciness_vertical = self.json_cfg["BOUNCINESS_VERTICAL"]
        self.cfg.bounciness_horizontal = self.json_cfg["BOUNCINESS_HORIZONTAL"]
        self.cfg.max_speed = self.json_cfg["MAX_SPEED"]
        self.cfg.fps = self.json_cfg["FPS"]

        # initial velocities
        self.cfg.initial_vx = self.json_cfg["SPEED_X"] * (1 if random.random() < 0.5 else -1)
        self.cfg.initial_vy = -self.json_cfg["INITIAL_VY"]

        # air drag
        self.cfg.enable_air_drag_x = int(self.json_cfg["ENABLE_AIR_DRAG_X"])
        self.cfg.enable_air_drag_y = int(self.json_cfg["ENABLE_AIR_DRAG_Y"])
        self.cfg.air_drag_x_rate = self.json_cfg["AIR_DRAG_X_RATE"]
        self.cfg.air_drag_y_rate = self.json_cfg["AIR_DRAG_Y_RATE"]
        self.cfg.air_drag_x_min_speed = self.json_cfg["AIR_DRAG_X_MIN_SPEED"]
        self.cfg.air_drag_y_min_speed = self.json_cfg["AIR_DRAG_Y_MIN_SPEED"]

        # spin torque
        self.cfg.enable_spin_torque = int(self.json_cfg["ENABLE_SPIN_TORQUE"])
        self.cfg.spin_torque_strength = self.json_cfg["SPIN_TORQUE_STRENGTH"]

        # squish
        self.cfg.squish_enabled = int(self.json_cfg["SQUISH_ENABLED"])
        self.cfg.squish_decay_rate = self.json_cfg["SQUISH_DECAY_RATE"]
        self.cfg.squish_factor = self.json_cfg["SQUISH_FACTOR"]
        self.cfg.squish_max = self.json_cfg["SQUISH_MAX"]

        # random impulse
        self.cfg.enable_random_impulse_x = int(self.json_cfg["ENABLE_RANDOM_IMPULSE_X"])
        self.cfg.enable_random_impulse_y = int(self.json_cfg["ENABLE_RANDOM_IMPULSE_Y"])
        self.cfg.rand_impulse_x_min = self.json_cfg["RANDOM_IMPULSE_X_MIN"]
        self.cfg.rand_impulse_x_max = self.json_cfg["RANDOM_IMPULSE_X_MAX"]
        self.cfg.rand_impulse_y_min = self.json_cfg["RANDOM_IMPULSE_Y_MIN"]
        self.cfg.rand_impulse_y_max = self.json_cfg["RANDOM_IMPULSE_Y_MAX"]
        self.cfg.rand_impulse_x_max_speed = self.json_cfg["RANDOM_IMPULSE_X_MAX_SPEED"]
        self.cfg.rand_impulse_y_max_speed = self.json_cfg["RANDOM_IMPULSE_Y_MAX_SPEED"]

        # bounce flicker
        self.cfg.enable_bounce_flicker = int(self.json_cfg["ENABLE_BOUNCE_FLICKER"])
        self.cfg.flicker_decay_rate = self.json_cfg["FLICKER_DECAY_RATE"]

        # impact squash
        self.cfg.enable_impact_squash = int(self.json_cfg["ENABLE_IMPACT_SQUASH"])
        self.cfg.impact_squash_mult = self.json_cfg["IMPACT_SQUASH_MULT"]
        self.cfg.impact_recovery_rate = self.json_cfg["IMPACT_RECOVERY_RATE"]

        # squish tilt
        self.cfg.enable_squish_tilt = int(self.json_cfg["ENABLE_SQUISH_TILT"])
        self.cfg.tilt_factor = self.json_cfg["TILT_FACTOR"]

        # magnetic squish
        self.cfg.enable_magnetic_squish = int(self.json_cfg["ENABLE_MAGNETIC_SQUISH"])
        self.cfg.magnetic_range = self.json_cfg["MAGNETIC_RANGE"]
        self.cfg.magnetic_strength = self.json_cfg["MAGNETIC_STRENGTH"]

        # jiggle
        self.cfg.enable_jiggle = int(self.json_cfg["ENABLE_JIGGLE"])
        self.cfg.jiggle_strength = self.json_cfg["JIGGLE_STRENGTH"]
        self.cfg.jiggle_freq = self.json_cfg["JIGGLE_FREQ"]
        self.cfg.jiggle_decay_rate = self.json_cfg["JIGGLE_DECAY_RATE"]

        # stuck / unsticking
        self.cfg.stuck_y_tolerance = self.json_cfg["STUCK_Y_TOLERANCE"]
        self.cfg.stuck_threshold_time = self.json_cfg["STUCK_THRESHOLD_TIME"]
        self.cfg.stuck_impulse_min = self.json_cfg["STUCK_IMPULSE_MIN"]
        self.cfg.stuck_impulse_max = self.json_cfg["STUCK_IMPULSE_MAX"]

        # radii
        self.cfg.ball_radius = self.json_cfg["BALL_RADIUS"]
        self.cfg.halo_radius = self.json_cfg["HALO_RADIUS"]

        # trail
        self.cfg.enable_trail_effect = int(self.json_cfg["ENABLE_TRAIL_EFFECT"])
        self.cfg.trail_new_color_percent = self.json_cfg["TRAIL_NEW_COLOR_PERCENT"]

        # color modes
        self.cfg.enable_rainbow_ball = int(self.json_cfg["ENABLE_RAINBOW_BALL"])
        self.cfg.enable_heatmap_glow = int(self.json_cfg["ENABLE_HEATMAP_GLOW"])

        # base colors
        self.cfg.ball_r = ball_r
        self.cfg.ball_g = ball_g
        self.cfg.ball_b = ball_b

        self.cfg.bg_r = bg_r
        self.cfg.bg_g = bg_g
        self.cfg.bg_b = bg_b

    def update_and_send_json(self):
        self.parse_json()
        self.lib.ParseConfig(ctypes.byref(self.cfg))

    def update(self, dt):
        if self.json_cfg["HOT_RELOAD"] == False: return
        self.last_check_debounce = self.last_check_debounce + dt
        if self.last_check_debounce >= 5:
            self.last_check_debounce = 0
            n_json_cfg = None
            with open(CONFIG_PATH, "r") as f:
                n_json_cfg = json.load(f)
            for key in n_json_cfg:
                if key == "BALL_COLOR":
                    n_ball_r, n_ball_g, n_ball_b = do_parse_rgb(n_json_cfg, "BALL_COLOR")
                    if n_ball_r != self.last_ball_r or \
                    n_ball_g != self.last_ball_g or \
                    n_ball_b != self.last_ball_b: 
                        self.update_and_send_json()
                        self.last_check_debounce = 0
                        return
                elif key == "BACKGROUND_COLOR":
                    n_bg_r, n_bg_g, n_bg_b = do_parse_rgb(n_json_cfg, "BACKGROUND_COLOR")
                    if n_bg_r != self.last_bg_r or \
                    n_bg_g != self.last_bg_g or \
                    n_bg_b != self.last_bg_b: 
                        self.update_and_send_json()
                        self.last_check_debounce = 0
                        return
                else:
                    if self.json_cfg[key] != n_json_cfg[key]:
                        self.update_and_send_json()
                        return
            self.last_check_debounce = 0