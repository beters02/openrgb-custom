local restart

restart = {

    callback = function(args, options)
        
    end,

    description = "Get the current value of a setting",

    -- the arg table contains strings which could be options, or types
    args = {},
    options = {t = "Restart as a test (if so, other options will be ignored)", v = "Toggle visualizer after restart", j = "Switch your current terminal to journalctl live feed after restart"},
    example = "setting_get BouncingBallWithSolidBackground BACKGROUND_COLOR"
}

return restart