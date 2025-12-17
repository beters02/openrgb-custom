local stdio = require("@lune/stdio")
local shared = require("./shared")

local function formatCommandName(commandName)
    return stdio.color("green")..commandName..stdio.color("reset")
end

local function formatArgumentName(argName)
    return stdio.color("cyan")..argName..stdio.color("reset")
end

local function formatOptionName(optionName)
    return stdio.color("purple")..optionName..stdio.color("reset")
end

local function formatKeyName(keyName)
    return stdio.color("yellow")..keyName..stdio.color("reset")
end

local function formatDescription(description)
    return stdio.color("blue")..description..stdio.color("reset")
end

local function printCommandInfo(commandName, commandObj)
    local i, v = commandName, commandObj

    -- print command name
    stdio.write("[ "..formatCommandName(commandName).." ]\n")

    -- if missing description, skip
    if not v.description then
        print(formatKeyName("description")..": [missing description]\n")
        return
    end

    -- print description
    print(formatKeyName("description")..": " .. formatDescription(v.description))

    -- if missing args, skip
    v.args = v.args or {}
    
    -- start print usage (args)
    local argsamnt = 0
    local usg = formatKeyName("usage")..": " .. formatCommandName(i).." ["..formatOptionName("-options").."]"

    -- make sure args are in right order
    local argsorder = v.argsorder
    if not argsorder then
        argsorder = {}
        for ai, _ in pairs(v.args) do
            table.insert(argsorder, ai)
        end
    end
    
    -- start print args
    if #argsorder > 0 then
        for ai = 1, #argsorder do
            argsamnt += 1
            
            local argname = argsorder[ai]
            local options = v.args[argname]

            -- print arg name
            usg = usg .. " {"..formatArgumentName(argname)

            -- start print options
            if #options > 0 then
                usg = usg .. "("
                for oi, opt in pairs(options) do
                    usg = usg..formatOptionName(opt)
                    if oi ~= #options then
                        usg = usg..", "
                    end
                end
                -- close options
                usg = usg..")"
            end

            -- close args
            usg = usg .. "}"
        end
    end

    -- print args and arg options
    print(usg)

    -- print all command options
    if v.options and #v.options >= 1 then
        local optstr = ""
        for optname, optdesc in pairs(v.options) do
            optstr=optstr.."\n"
            optstr=formatArgumentName(optname)..": "..formatDescription(optdesc)
        end
        print("\n")
        print(formatKeyName("options: ")..optstr)
    end

    -- start print example if necessary
    if argsamnt > 0 then

        -- if there are args, an example is required.
        -- we skip if no example provided
        if not v.example then
            print(formatKeyName("example")..": " .. i .. " [missing example]\n")
            return
        end
        
        local exctr = 0
        local exstr = formatKeyName("example")..": "
        for word in v.example:gmatch("%w+") do
            exctr += 1

            -- first word is the command
            if exctr == 1 then
                exstr = exstr .. formatCommandName(word).." "
            else

                -- all others are arguments
                exstr = exstr .. formatArgumentName(word).." "
            end
        end

        -- get rid of the final space
        exstr = exstr:sub(1, exstr:len()-1)

        -- print example
        print(exstr.."\n")
        return
    end

    -- if an example is not needed, make sure we print the final line
    print("")
end

local function copyTblNoFunctions(t)
    local n = {}
    for i, v in pairs(t) do
        if typeof(v) == "table" then
            n[i] = copyTblNoFunctions(v)
            continue
        end
        if i == "callback" then
            continue
        end
        n[i] = v
    end
    return n
end

local help = {}

-- CUSTOM PROPERTIES AND METHODS
help.commands = {}
help.printOrder = {}

-- OPTIONAL PROPERTIES AND METHODS

--argsorder = {} -- only for command with args
--options = {} -- add options like -o

help.init = function(commands, printOrder)
    help.commands = copyTblNoFunctions(commands)
    help.printOrder = printOrder
end

-- NEEDED PROPERTIES AND METHODS

-- example = "push linux all game" -- only for commands with args
help.description = "List all commands"
help.args = {}
help.callback = function()
    print("\n\n\n")
    shared.printNameAndVersionSeperator(true)
    print("")

    -- ordered
    for i, v in ipairs(help.printOrder) do
        if string.sub(v, 1, 1) == "_" then continue end
        printCommandInfo(v, help.commands[v])
    end

    -- unordered
    for i, v in pairs(help.commands) do
        if table.find(help.printOrder, i) then
            continue
        end
        printCommandInfo(i, v)
    end

    shared.printSeperator(4)
    print(stdio.color("red").."TUTORIALS:"..stdio.color("reset"))
    print(formatDescription("To view a list of tutorials, run the tutorial command."))
    shared.printSeperator(4)
end

return help