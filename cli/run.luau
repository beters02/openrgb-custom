local process = require("@lune/process")
local commands = require("./commands")
local color = require("../color")

local args = process.args
if args[1] == nil then
    commands.help.callback()
elseif not commands[args[1]] then
    print(color.colorln("r", "Command " .. args[1] .. " does not exist. Run the help command to list all commands."))
else
    -- get options
    local newArgs = {}
    local options = {}
    for i, v in ipairs(args) do
        if v:sub(1, 1) == "-" then
            options[v:sub(2, v:len())] = true
        else
            -- remove options from final args table
            table.insert(newArgs, v)
        end
    end
    commands[args[1]].callback(newArgs, options)
end

return nil