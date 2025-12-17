import os
import json
import random

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

class CFGHelper:
    def __init__(self):
        with open(CONFIG_PATH, "r") as f:
            self.json_cfg = json.load(f)

    def parse_rgb(self, name: str):
        v = self.json_cfg[name]
        if isinstance(v, list) and len(v) == 4 and v[0] == "RGBColor":
            return int(v[1]), int(v[2]), int(v[3])
        raise ValueError(f"Config field {name} must be ['RGBColor', r, g, b]")

    def parse_json(self, cfg):
        ball_r, ball_g, ball_b = self.parse_rgb("BALL_COLOR")
        bg_r, bg_g, bg_b = self.parse_rgb("BACKGROUND_COLOR")

        cfg.gravity = self.json_cfg["GRAVITY"]
        cfg.bounciness_vertical = self.json_cfg["BOUNCINESS_VERTICAL"]
        cfg.bounciness_horizontal = self.json_cfg["BOUNCINESS_HORIZONTAL"]
        cfg.max_speed = self.json_cfg["MAX_SPEED"]
        cfg.fps = self.json_cfg["FPS"]

        # initial velocities
        cfg.initial_vx = self.json_cfg["SPEED_X"] * (1 if random.random() < 0.5 else -1)
        cfg.initial_vy = -self.json_cfg["INITIAL_VY"]

        # air drag
        cfg.enable_air_drag_x = int(self.json_cfg["ENABLE_AIR_DRAG_X"])
        cfg.enable_air_drag_y = int(self.json_cfg["ENABLE_AIR_DRAG_Y"])
        cfg.air_drag_x_rate = self.json_cfg["AIR_DRAG_X_RATE"]
        cfg.air_drag_y_rate = self.json_cfg["AIR_DRAG_Y_RATE"]
        cfg.air_drag_x_min_speed = self.json_cfg["AIR_DRAG_X_MIN_SPEED"]
        cfg.air_drag_y_min_speed = self.json_cfg["AIR_DRAG_Y_MIN_SPEED"]

        # spin torque
        cfg.enable_spin_torque = int(self.json_cfg["ENABLE_SPIN_TORQUE"])
        cfg.spin_torque_strength = self.json_cfg["SPIN_TORQUE_STRENGTH"]

        # squish
        cfg.squish_enabled = int(self.json_cfg["SQUISH_ENABLED"])
        cfg.squish_decay_rate = self.json_cfg["SQUISH_DECAY_RATE"]
        cfg.squish_factor = self.json_cfg["SQUISH_FACTOR"]
        cfg.squish_max = self.json_cfg["SQUISH_MAX"]

        # random impulse
        cfg.enable_random_impulse_x = int(self.json_cfg["ENABLE_RANDOM_IMPULSE_X"])
        cfg.enable_random_impulse_y = int(self.json_cfg["ENABLE_RANDOM_IMPULSE_Y"])
        cfg.rand_impulse_x_min = self.json_cfg["RANDOM_IMPULSE_X_MIN"]
        cfg.rand_impulse_x_max = self.json_cfg["RANDOM_IMPULSE_X_MAX"]
        cfg.rand_impulse_y_min = self.json_cfg["RANDOM_IMPULSE_Y_MIN"]
        cfg.rand_impulse_y_max = self.json_cfg["RANDOM_IMPULSE_Y_MAX"]
        cfg.rand_impulse_x_max_speed = self.json_cfg["RANDOM_IMPULSE_X_MAX_SPEED"]
        cfg.rand_impulse_y_max_speed = self.json_cfg["RANDOM_IMPULSE_Y_MAX_SPEED"]

        # bounce flicker
        cfg.enable_bounce_flicker = int(self.json_cfg["ENABLE_BOUNCE_FLICKER"])
        cfg.flicker_decay_rate = self.json_cfg["FLICKER_DECAY_RATE"]

        # impact squash
        cfg.enable_impact_squash = int(self.json_cfg["ENABLE_IMPACT_SQUASH"])
        cfg.impact_squash_mult = self.json_cfg["IMPACT_SQUASH_MULT"]
        cfg.impact_recovery_rate = self.json_cfg["IMPACT_RECOVERY_RATE"]

        # squish tilt
        cfg.enable_squish_tilt = int(self.json_cfg["ENABLE_SQUISH_TILT"])
        cfg.tilt_factor = self.json_cfg["TILT_FACTOR"]

        # magnetic squish
        cfg.enable_magnetic_squish = int(self.json_cfg["ENABLE_MAGNETIC_SQUISH"])
        cfg.magnetic_range = self.json_cfg["MAGNETIC_RANGE"]
        cfg.magnetic_strength = self.json_cfg["MAGNETIC_STRENGTH"]

        # jiggle
        cfg.enable_jiggle = int(self.json_cfg["ENABLE_JIGGLE"])
        cfg.jiggle_strength = self.json_cfg["JIGGLE_STRENGTH"]
        cfg.jiggle_freq = self.json_cfg["JIGGLE_FREQ"]
        cfg.jiggle_decay_rate = self.json_cfg["JIGGLE_DECAY_RATE"]

        # stuck / unsticking
        cfg.stuck_y_tolerance = self.json_cfg["STUCK_Y_TOLERANCE"]
        cfg.stuck_threshold_time = self.json_cfg["STUCK_THRESHOLD_TIME"]
        cfg.stuck_impulse_min = self.json_cfg["STUCK_IMPULSE_MIN"]
        cfg.stuck_impulse_max = self.json_cfg["STUCK_IMPULSE_MAX"]

        # radii
        cfg.ball_radius = self.json_cfg["BALL_RADIUS"]
        cfg.halo_radius = self.json_cfg["HALO_RADIUS"]

        # trail
        cfg.enable_trail_effect = int(self.json_cfg["ENABLE_TRAIL_EFFECT"])
        cfg.trail_new_color_percent = self.json_cfg["TRAIL_NEW_COLOR_PERCENT"]

        # color modes
        cfg.enable_rainbow_ball = int(self.json_cfg["ENABLE_RAINBOW_BALL"])
        cfg.enable_heatmap_glow = int(self.json_cfg["ENABLE_HEATMAP_GLOW"])

        # base colors
        cfg.ball_r = ball_r
        cfg.ball_g = ball_g
        cfg.ball_b = ball_b

        cfg.bg_r = bg_r
        cfg.bg_g = bg_g
        cfg.bg_b = bg_b