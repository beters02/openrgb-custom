local stdio = require("@lune/stdio")

local colors = {g = "green", b = "blue", y = "yellow", blk = "black", c = "cyan", p = "purple", r = "red", x = "reset", w = "white"}

local cm = {}

function cm.color(c)
    return stdio.color(colors[c] or c)
end

function cm.colorln(c, msg)
    return cm.color(c)..msg..cm.color("x")
end

return cm