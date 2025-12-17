local fs = require("@lune/fs")

local list

list = {

    callback = function(args, options)
        for i, v in pairs(fs.readDir("./effects")) do
            print(v)
        end
    end,

    description = "List all effects",

    -- the arg table contains strings which could be options, or types
    args = {}
}

return list