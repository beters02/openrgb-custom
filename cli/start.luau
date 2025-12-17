--local fs = require("@lune/fs")
--local process = require("@lune/process")
local shared = require("./shared")

local start

start = {

    callback = function(args, options)
        return shared.start(args[2], options)
    end,

    description = "Start an effect",

    -- the arg table contains strings which could be options, or types
    args = {effect = {"effect", "string"}},
    argsorder = {"effect"},
    options = {t = "Restart as a test (if so, other options will be ignored)", v = "Toggle visualizer automatically"},
    example = "start BouncingBallWithSolidBackground"
}


return start