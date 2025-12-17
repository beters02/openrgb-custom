-- this is where shared command functions live

local fs = require("@lune/fs")
local stdio = require("@lune/stdio")
local process = require("@lune/process")
local config = require("../config")
local task = require("@lune/task")

local shared

shared = {
    seperator = "----------",
    namestr = stdio.color("green")..config.project_name..stdio.color("reset"),
    vstr = stdio.color("red").."V"..config.project_version..stdio.color("reset"),
    descstr = stdio.color("blue")..config.project_description..stdio.color("reset"),

    printNameAndVersion = function(brackets)
        local str = shared.namestr.." "..shared.vstr
        if brackets then
            brackets = {brackets:sub(1,1), brackets:sub(2,2)}
            str = brackets[1].." "..str.." "..brackets[2]
        end
        print(str)
    end,

    printNameAndVersionSeperator = function(includeDescription)
        shared.printSeperator(4)
        
        local str = shared.namestr.." "..shared.vstr
        local spaces = shared.seperator:len()*4
        spaces -= math.round(str:len())
        for i = 1, spaces + 4 do
            str = " " .. str
        end
        print(str)

        if includeDescription then
            local dstr = shared.descstr
            local dspaces = shared.seperator:len()*4
            dspaces -= math.round(shared.descstr:len())
            for i = 1, dspaces do
                dstr = " "..dstr
            end
            print(dstr)
        end

        shared.printSeperator(4)
    end,

    printDescription = function(brackets)
        local str = shared.descstr
        if brackets then
            brackets = {brackets:sub(1,1), brackets:sub(2,2)}
            str = brackets[1].." "..str.." "..brackets[2]
        end
        print(str)
    end,

    printSeperator = function(amount)
        local str = ""
        amount = amount or 1
        for i = 1, amount do
            str = str .. shared.seperator
        end
        print(str)
    end,

    startTest = function()
        shared.start("BouncingBallWithSolidBackground", {v = true})
    end,

    start = function(effect, options)

        if options["t"] then
            return shared.startTest()
        end

        if effect == nil then
            print("start command must have an effect!")
            return
        end

        if not fs.readDir(config.project_path.."/effects/"..effect) then
            error(effect.." does not exist.")
        end

        if options["v"] then
            task.delay(3, function()
                process.create("./toggle_visualizer.sh", {}, {cwd = config.project_path.."/bin"})
            end)
        end

        process.exec(config.project_path.."/bin/run_effect.sh", {effect}, {stdio = "forward"})
        return
    end
}

return shared