local fs = require("@lune/fs")
local process = require("@lune/process")
local config = require("../config")

local toggle_visualizer

toggle_visualizer = {
    callback = function(args, options)
        if not fs.isDir(config.project_path.."/effects/Visualizer") then
            error("Visualizer effect does not exist.")
        end

        process.exec(config.project_path.."/bin/toggle_visualizer.sh", {}, {stdio = "forward"})
    end,

    description = "Toggle the keyboard visualizer if the effect supports it.",
    args = {},
}

return toggle_visualizer