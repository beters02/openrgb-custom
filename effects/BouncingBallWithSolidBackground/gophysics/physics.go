package main

/*
#include <stdint.h>

typedef struct {
    // ---- core physics / timing ----
    double gravity;
    double bounciness_vertical;
    double bounciness_horizontal;
    double max_speed;
    double fps;

    // initial velocity
    double initial_vx;
    double initial_vy;

    // ---- air drag (per-second rates) ----
    int    enable_air_drag_x;
    int    enable_air_drag_y;
    double air_drag_x_rate;
    double air_drag_y_rate;
	double air_drag_x_min_speed;
    double air_drag_y_min_speed;

    // ---- spin torque ----
    int    enable_spin_torque;
    double spin_torque_strength;

    // ---- squish ----
    int    squish_enabled;
    double squish_decay_rate; // per second
    double squish_factor;
    double squish_max;

    // ---- random impulse on bounce ----
    int    enable_random_impulse_x;
	int    enable_random_impulse_y;
    double rand_impulse_x_min;
    double rand_impulse_x_max;
    double rand_impulse_y_min;
    double rand_impulse_y_max;
	double rand_impulse_x_max_speed;
	double rand_impulse_y_max_speed;

    // ---- bounce flicker ----
    int    enable_bounce_flicker;
    double flicker_decay_rate; // per second

    // ---- impact squash ----
    int    enable_impact_squash;
    double impact_squash_mult;
    double impact_recovery_rate; // per second

    // ---- squish tilt ----
    int    enable_squish_tilt;
    double tilt_factor;

    // ---- magnetic squish ----
    int    enable_magnetic_squish;
    double magnetic_range;
    double magnetic_strength;

    // ---- jiggle ----
    int    enable_jiggle;
    double jiggle_strength;
    double jiggle_freq;
    double jiggle_decay_rate; // per second

    // ---- stuck / unsticking ----
    double stuck_y_tolerance;
    double stuck_threshold_time;
    double stuck_impulse_min;
    double stuck_impulse_max;

    // ---- rendering radii ----
    double ball_radius;
    double halo_radius;

    // ---- trail ----
    int    enable_trail_effect;
    double trail_new_color_percent; // 0..1

    // ---- color modes ----
    int    enable_rainbow_ball;
    int    enable_heatmap_glow;

    // BALL_COLOR
    uint8_t ball_r;
    uint8_t ball_g;
    uint8_t ball_b;

    // BACKGROUND_COLOR
    uint8_t bg_r;
    uint8_t bg_g;
    uint8_t bg_b;
} EffectConfig;
*/
import "C"

import (
	"adv_bounce_effect/printutil"
	"math"
	"math/rand"
	"time"
	"unsafe"
)

// -----------------------
// helpers
// -----------------------

type vec2 struct {
	x, y float64
}

type color struct {
	r, g, b uint8
}

func clampByte(v float64) uint8 {
	if v < 0 {
		return 0
	}
	if v > 255 {
		return 255
	}
	return uint8(v + 0.5)
}

func lerpColor(c1, c2 color, t float64) color {
	if t < 0 {
		t = 0
	} else if t > 1 {
		t = 1
	}
	return color{
		r: clampByte(float64(c1.r) + (float64(c2.r)-float64(c1.r))*t),
		g: clampByte(float64(c1.g) + (float64(c2.g)-float64(c1.g))*t),
		b: clampByte(float64(c1.b) + (float64(c2.b)-float64(c1.b))*t),
	}
}

func hsvToRGB(h, s, v float64) color {
	h = math.Mod(h, 1.0) * 6.0
	c := v * s
	x := c * (1 - math.Abs(math.Mod(h, 2)-1))
	var r, g, b float64
	switch {
	case h < 1:
		r, g, b = c, x, 0
	case h < 2:
		r, g, b = x, c, 0
	case h < 3:
		r, g, b = 0, c, x
	case h < 4:
		r, g, b = 0, x, c
	case h < 5:
		r, g, b = x, 0, c
	default:
		r, g, b = c, 0, x
	}
	m := v - c
	return color{
		r: clampByte((r + m) * 255),
		g: clampByte((g + m) * 255),
		b: clampByte((b + m) * 255),
	}
}

func cBool(v C.int) bool { return v != 0 }

func expDecay(rate, dt float64) float64 {
	if rate <= 0 || dt <= 0 {
		return 1.0
	}
	return math.Exp(-rate * dt)
}

func debugPrint[T printutil.Printable](prefix string, msg T) {
	printutil.Stdout(prefix + ": ")
	printutil.Stdout(msg)
}

// -----------------------
// global state
// -----------------------

type EffectConfigGo struct {
	gravity, bouncV, bouncH, maxSpeed float64
	fps                               float64

	initialVX, initialVY float64

	airDragX, airDragY bool
	airDragXRate       float64
	airDragYRate       float64
	airDragXMinSpeed   float64
	airDragYMinSpeed   float64

	spinTorque       bool
	spinTorqueAmount float64

	squishEnabled   bool
	squishDecayRate float64
	squishFactor    float64
	squishMax       float64

	randImpulseX, randImpulseY bool
	rxMin, rxMax               float64
	ryMin, ryMax               float64
	rxMaxSpeed, ryMaxSpeed     float64

	bounceFlicker    bool
	flickerDecayRate float64

	impactSquash       bool
	impactMult         float64
	impactRecoveryRate float64

	squishTilt bool
	tiltFactor float64

	magneticSquish   bool
	magneticRange    float64
	magneticStrength float64

	jiggle          bool
	jiggleStrength  float64
	jiggleFreq      float64
	jiggleDecayRate float64

	stuckYTol, stuckThresh   float64
	stuckImpMin, stuckImpMax float64

	ballRadius, haloRadius float64

	trailEnabled         bool
	trailNewColorPercent float64

	rainbowBall bool
	heatmapGlow bool
	ballColor   color
	bgColor     color
}

var (
	gCfg      EffectConfigGo
	gLEDCount int

	gPositions []vec2
	gColors    []color
	gTrail     []color

	ballX, ballY float64
	vx, vy       float64
	squish       float64

	impactSX, impactSY float64
	impactAxis         int // 0 none, 1 vertical wall, 2 horizontal wall

	jiggleAmount float64
	jigglePhase  float64

	stuckTime       float64
	flickerStrength float64

	minX, maxX float64
	minY, maxY float64

	initialized bool
)

// -----------------------
// layout
// -----------------------

func defaultLEDPositions(ledCount int) []vec2 {
	m := map[int]vec2{
		// Row 0 - Function row
		37: {0, 0}, 54: {1, 0}, 55: {2, 0}, 56: {3, 0}, 57: {4, 0},
		58: {6, 0}, 59: {7, 0}, 60: {8, 0}, 61: {9, 0},
		62: {11, 0}, 63: {12, 0}, 64: {13, 0}, 65: {14, 0},
		66: {15, 0}, 67: {16, 0}, 68: {17, 0},

		// Row 1 - Number row
		49: {0, 1}, 26: {1, 1}, 27: {2, 1}, 28: {3, 1}, 29: {4, 1},
		30: {5, 1}, 31: {6, 1}, 32: {7, 1}, 33: {8, 1}, 34: {9, 1},
		35: {10, 1}, 41: {11, 1}, 42: {12, 1}, 38: {13.5, 1},
		69: {14, 1}, 70: {15, 1}, 71: {16, 1},

		// Row 2 - Q row
		39: {0, 2}, 16: {1, 2}, 22: {2, 2}, 4: {3, 2}, 17: {4, 2},
		19: {5, 2}, 24: {6, 2}, 20: {7, 2}, 8: {8, 2}, 14: {9, 2},
		15: {10, 2}, 43: {11, 2}, 44: {12, 2}, 45: {13, 2},
		72: {14, 2}, 73: {15, 2}, 74: {16, 2},

		// Row 3 - A row
		53: {0, 3}, 0: {1, 3}, 18: {2, 3}, 3: {3, 3}, 5: {4, 3}, 6: {5, 3},
		7: {6, 3}, 9: {7, 3}, 10: {8, 3}, 11: {9, 3},
		47: {10, 3}, 48: {11, 3}, 46: {12, 3}, 36: {13.5, 3},

		// Row 4 - Z row
		82: {0, 4}, 79: {1, 4}, 25: {2, 4}, 23: {3, 4}, 2: {4, 4}, 21: {5, 4},
		1: {6, 4}, 13: {7, 4}, 12: {8, 4},
		50: {9, 4}, 51: {10, 4}, 52: {11, 4},
		86: {13, 4}, 78: {15, 4},

		// Row 5 - bottom row
		81: {0, 5}, 84: {1, 5}, 83: {2, 5},
		40: {5, 5}, // space

		87: {8, 5},  // right alt
		88: {9, 5},  // right fn
		80: {10, 5}, // menu
		85: {12, 5}, // right ctrl

		76: {14, 5}, 77: {15, 5}, 75: {16, 5},

		// Logo + indicators
		89: {0, -1},
		90: {16, -1},
		91: {17, -1},
		92: {0, -0.3},
		93: {8, -0.3},
	}

	positions := make([]vec2, ledCount)
	for i := 0; i < ledCount; i++ {
		if p, ok := m[i]; ok {
			positions[i] = p
		} else {
			positions[i] = vec2{0, 0}
		}
	}
	return positions
}

func computeBounds(includeNegative bool) (float64, float64, float64, float64) {
	if len(gPositions) == 0 {
		return 0, 0, 0, 0
	}
	minx, maxx := gPositions[0].x, gPositions[0].x
	miny, maxy := gPositions[0].y, gPositions[0].y
	for _, p := range gPositions {
		if !includeNegative && p.y < 0 {
			continue
		}
		if p.x < minx {
			minx = p.x
		}
		if p.x > maxx {
			maxx = p.x
		}
		if p.y < miny {
			miny = p.y
		}
		if p.y > maxy {
			maxy = p.y
		}
	}
	return minx, maxx, miny, maxy
}

// -----------------------
// exported: ParseConfig
// -----------------------

//export ParseConfig
func ParseConfig(cfg *C.EffectConfig) {
	gCfg = EffectConfigGo{
		gravity:   float64(cfg.gravity),
		bouncV:    float64(cfg.bounciness_vertical),
		bouncH:    float64(cfg.bounciness_horizontal),
		maxSpeed:  float64(cfg.max_speed),
		fps:       float64(cfg.fps),
		initialVX: float64(cfg.initial_vx),
		initialVY: float64(cfg.initial_vy),

		airDragX:         cBool(cfg.enable_air_drag_x),
		airDragY:         cBool(cfg.enable_air_drag_y),
		airDragXRate:     float64(cfg.air_drag_x_rate),
		airDragYRate:     float64(cfg.air_drag_y_rate),
		airDragXMinSpeed: float64(cfg.air_drag_x_min_speed),
		airDragYMinSpeed: float64(cfg.air_drag_y_min_speed),

		spinTorque:       cBool(cfg.enable_spin_torque),
		spinTorqueAmount: float64(cfg.spin_torque_strength),

		squishEnabled:   cBool(cfg.squish_enabled),
		squishDecayRate: float64(cfg.squish_decay_rate),
		squishFactor:    float64(cfg.squish_factor),
		squishMax:       float64(cfg.squish_max),

		randImpulseX: cBool(cfg.enable_random_impulse_x),
		randImpulseY: cBool(cfg.enable_random_impulse_y),
		rxMin:        float64(cfg.rand_impulse_x_min),
		rxMax:        float64(cfg.rand_impulse_x_max),
		ryMin:        float64(cfg.rand_impulse_y_min),
		ryMax:        float64(cfg.rand_impulse_y_max),
		rxMaxSpeed:   float64(cfg.rand_impulse_x_max_speed),
		ryMaxSpeed:   float64(cfg.rand_impulse_y_max_speed),

		bounceFlicker:    cBool(cfg.enable_bounce_flicker),
		flickerDecayRate: float64(cfg.flicker_decay_rate),

		impactSquash:       cBool(cfg.enable_impact_squash),
		impactMult:         float64(cfg.impact_squash_mult),
		impactRecoveryRate: float64(cfg.impact_recovery_rate),

		squishTilt: cBool(cfg.enable_squish_tilt),
		tiltFactor: float64(cfg.tilt_factor),

		magneticSquish:   cBool(cfg.enable_magnetic_squish),
		magneticRange:    float64(cfg.magnetic_range),
		magneticStrength: float64(cfg.magnetic_strength),

		jiggle:          cBool(cfg.enable_jiggle),
		jiggleStrength:  float64(cfg.jiggle_strength),
		jiggleFreq:      float64(cfg.jiggle_freq),
		jiggleDecayRate: float64(cfg.jiggle_decay_rate),

		stuckYTol:            float64(cfg.stuck_y_tolerance),
		stuckThresh:          float64(cfg.stuck_threshold_time),
		stuckImpMin:          float64(cfg.stuck_impulse_min),
		stuckImpMax:          float64(cfg.stuck_impulse_max),
		ballRadius:           float64(cfg.ball_radius),
		haloRadius:           float64(cfg.halo_radius),
		trailEnabled:         cBool(cfg.enable_trail_effect),
		trailNewColorPercent: float64(cfg.trail_new_color_percent),
		rainbowBall:          cBool(cfg.enable_rainbow_ball),
		heatmapGlow:          cBool(cfg.enable_heatmap_glow),
		ballColor: color{
			r: uint8(cfg.ball_r),
			g: uint8(cfg.ball_g),
			b: uint8(cfg.ball_b),
		},
		bgColor: color{
			r: uint8(cfg.bg_r),
			g: uint8(cfg.bg_g),
			b: uint8(cfg.bg_b),
		},
	}
}

// -----------------------
// exported: InitEffect
// -----------------------

//export InitEffect
func InitEffect(cfg *C.EffectConfig, ledCount C.int) {
	rand.Seed(time.Now().UnixNano())

	gLEDCount = int(ledCount)
	if gLEDCount <= 0 {
		return
	}

	ParseConfig(cfg)

	gPositions = defaultLEDPositions(gLEDCount)
	gColors = make([]color, gLEDCount)
	gTrail = make([]color, gLEDCount)

	minX, maxX, minY, maxY = computeBounds(true)

	// initial ball placement + velocity
	ballX = (minX + maxX) / 2
	ballY = (minY + maxY) * 0.25
	vx = gCfg.initialVX
	vy = gCfg.initialVY

	squish = 0
	impactSX, impactSY = 1, 1
	impactAxis = 0
	jiggleAmount, jigglePhase = 0, 0
	stuckTime = 0
	flickerStrength = 0

	initialized = true
}

// -----------------------
// exported: StepEffect
// -----------------------

//export StepEffect
func StepEffect(dt C.double, now C.double) {
	if !initialized || gLEDCount == 0 {
		return
	}

	d := float64(dt)
	if d <= 0 {
		if gCfg.fps > 0 {
			d = 1.0 / gCfg.fps
		} else {
			d = 1.0 / 60.0
		}
	}
	t := float64(now)
	c := gCfg

	// --- physics integration ---

	// horizontal
	ballX += vx * d
	// vertical with gravity
	vy += c.gravity * d
	ballY += vy * d

	// spin torque
	if c.spinTorque {
		vx += c.spinTorqueAmount * math.Sin(ballY*0.15+t*0.2)
	}

	// squish decay
	if c.squishEnabled && c.squishDecayRate > 0 {
		squish *= expDecay(c.squishDecayRate, d)
	}

	bounced := false
	impactAxis = 0

	// vertical walls
	if ballX < minX {
		ballX = minX + (minX - ballX)
		vx = -vx * c.bouncV
		bounced = true
		impactAxis = 1
	} else if ballX > maxX {
		ballX = maxX - (ballX - maxX)
		vx = -vx * c.bouncV
		bounced = true
		impactAxis = 1
	}

	// horizontal walls
	if ballY < minY {
		ballY = minY + (minY - ballY)
		vy = -vy * c.bouncH
		bounced = true
		impactAxis = 2
	} else if ballY > maxY {
		ballY = maxY - (ballY - maxY)
		vy = -vy * c.bouncH
		bounced = true
		impactAxis = 2
	}

	// prevent tiny micro-bounces
	if math.Abs(vy) < 1e-4 {
		vy = -2.0 - 3.0*rand.Float64()
	}

	// stuck detection (bottom)
	if ballY > (maxY - c.stuckYTol) {
		stuckTime += d
	} else {
		stuckTime = 0
	}
	if stuckTime > c.stuckThresh {
		impulse := c.stuckImpMin + rand.Float64()*(c.stuckImpMax-c.stuckImpMin)
		vy -= impulse
		stuckTime = 0
	}

	// flicker
	if bounced && c.bounceFlicker {
		flickerStrength = 1.0
	}
	if c.flickerDecayRate > 0 {
		flickerStrength *= expDecay(c.flickerDecayRate, d)
	}

	// squish from vertical impact speed
	if bounced && c.squishEnabled {
		impact := math.Min(c.squishMax, math.Abs(vy)*c.squishFactor)
		if impact > squish {
			squish = impact
		}
	}

	// impact squash
	if c.impactSquash {
		force := math.Min(1.0, math.Abs(vx+vy))
		strength := 1.0 + force*c.impactMult
		if impactAxis == 1 { // side walls
			impactSX = 1.0 / strength
			impactSY = strength
		} else if impactAxis == 2 { // floor / ceiling
			impactSY = 1.0 / strength
			impactSX = strength
		}

		// dt-based recovery back toward 1.0
		if c.impactRecoveryRate > 0 {
			alpha := 1.0 - expDecay(c.impactRecoveryRate, d)
			impactSX += (1.0 - impactSX) * alpha
			impactSY += (1.0 - impactSY) * alpha
		}
	} else {
		impactSX, impactSY = 1.0, 1.0
	}

	// jiggle
	if c.jiggle && bounced {
		jiggleAmount = math.Abs(vx+vy) * c.jiggleStrength
		jigglePhase = rand.Float64() * math.Pi * 2
	}
	if c.jiggle && c.jiggleDecayRate > 0 {
		jiggleAmount *= expDecay(c.jiggleDecayRate, d)
	} else if !c.jiggle {
		jiggleAmount = 0
	}

	// random impulse on bounce
	if bounced {
		if impactAxis == 1 && c.randImpulseX && vx < c.rxMaxSpeed {
			vx += c.rxMin + rand.Float64()*(c.rxMax-c.rxMin)
		}
		if impactAxis == 2 && c.randImpulseY && vy < c.ryMaxSpeed {
			impulse := c.ryMin + rand.Float64()*(c.ryMax-c.ryMin)
			vy += impulse
		}
	}

	// dt-based air drag
	if c.airDragX && c.airDragXRate > 0 && vx >= c.airDragXMinSpeed {
		vx *= expDecay(c.airDragXRate, d)
	}
	if c.airDragY && c.airDragYRate > 0 && vy >= c.airDragYMinSpeed {
		vy *= expDecay(c.airDragYRate, d)
	}

	// speed cap
	if vx > c.maxSpeed {
		vx = c.maxSpeed
	} else if vx < -c.maxSpeed {
		vx = -c.maxSpeed
	}

	if vy > c.maxSpeed {
		vy = c.maxSpeed
	} else if vy < -c.maxSpeed {
		vy = -c.maxSpeed
	}

	// ------------------------
	// rendering (per-LED)
	// ------------------------

	var core color
	if c.rainbowBall {
		core = hsvToRGB(math.Mod(t*0.2, 1.0), 1.0, 1.0)
	} else {
		core = c.ballColor
	}

	if c.heatmapGlow {
		heat := math.Min(1.0, math.Abs(vy)/40.0)
		hot := color{255, 30, 30}
		core = lerpColor(c.ballColor, hot, heat)
	}

	for i, p := range gPositions {
		dx := p.x - ballX
		dy := p.y - ballY

		// tilt & squish
		tilt := 0.0
		if c.squishTilt {
			tilt = vx * c.tiltFactor
		}

		sx, sy := 1.0, 1.0

		if c.magneticSquish {
			proxX := math.Min(math.Abs(ballX-minX), math.Abs(ballX-maxX))
			proxY := math.Min(math.Abs(ballY-minY), math.Abs(ballY-maxY))
			magX := math.Max(0, 1-(proxX/c.magneticRange))
			magY := math.Max(0, 1-(proxY/c.magneticRange))
			sx *= 1 - magX*c.magneticStrength
			sy *= 1 - magY*c.magneticStrength
		}

		if c.jiggle && jiggleAmount > 0 {
			j := jiggleAmount * math.Sin(t*c.jiggleFreq+jigglePhase)
			sx *= 1 + j
			sy *= 1 - j
		}

		if c.impactSquash {
			sx *= impactSX
			sy *= impactSY
		}

		var dist float64
		if c.squishEnabled {
			cosA := math.Cos(tilt)
			sinA := math.Sin(tilt)
			rx := dx*cosA - dy*sinA
			ry := dx*sinA + dy*cosA

			radiusX := c.ballRadius * (1 + squish*0.8)
			radiusY := c.ballRadius * (1 - squish)
			if radiusY < c.ballRadius*0.25 {
				radiusY = c.ballRadius * 0.25
			}

			rx /= sx
			ry /= sy

			// normalized elliptical distance, then scale like original radius
			dist = math.Sqrt((rx*rx)/(radiusX*radiusX)+(ry*ry)/(radiusY*radiusY)) * c.ballRadius
		} else {
			dist = math.Hypot(dx, dy)
		}

		var col color
		if dist <= c.ballRadius {
			col = core
		} else if dist <= c.haloRadius {
			soft := 1.0 - (dist-c.ballRadius)/(c.haloRadius-c.ballRadius)
			soft *= soft
			col = lerpColor(c.bgColor, core, soft)
		} else {
			col = c.bgColor
		}

		if flickerStrength > 0 && c.bounceFlicker {
			factor := 1 + flickerStrength*(rand.Float64()*0.6-0.3)
			col = color{
				r: clampByte(float64(col.r) * factor),
				g: clampByte(float64(col.g) * factor),
				b: clampByte(float64(col.b) * factor),
			}
		}

		gColors[i] = col
	}

	// trail
	if c.trailEnabled {
		t := c.trailNewColorPercent
		for i := 0; i < gLEDCount; i++ {
			gColors[i] = lerpColor(gTrail[i], gColors[i], t)
		}
		copy(gTrail, gColors)
	} else {
		copy(gTrail, gColors)
	}
}

// -----------------------
// exported: GetFrame
// -----------------------

//export GetFrame
func GetFrame(posOut *C.double, colOut *C.uchar) {
	if !initialized || gLEDCount == 0 {
		return
	}

	// positions: [x0, y0, x1, y1, ...]
	goPos := unsafe.Slice((*float64)(unsafe.Pointer(posOut)), gLEDCount*2)
	for i, p := range gPositions {
		goPos[i*2] = p.x
		goPos[i*2+1] = p.y
	}

	// colors: [r0, g0, b0, r1, g1, b1, ...]
	goCol := unsafe.Slice((*uint8)(unsafe.Pointer(colOut)), gLEDCount*3)
	for i, c := range gColors {
		goCol[i*3] = c.r
		goCol[i*3+1] = c.g
		goCol[i*3+2] = c.b
	}
}

func main() {}
