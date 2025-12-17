local shared = require("./shared")

local test

test = {
    callback = function(args, options)
        shared.startTest()
    end,

    description = "Start a test",

    args = {}
}

return test