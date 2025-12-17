-- this is where you register commands

local commands = {}
local help = require("./help")
local setting_set = require("./setting_set")
local setting_get = require("./setting_get")
local list = require("./list")
local start = require("./start")
local toggle_visualizer = require("./toggle_visualizer")
local test = require("./test")

commands.help = help
commands.setting_set = setting_set
commands.setting_get = setting_get
commands.list = list
commands.start = start
commands.toggle_visualizer = toggle_visualizer
commands.test = test

-- if you need to init a command for any reason, do this here.
help.init(commands, {"help"}) -- add list order secondly

return commands