-- convert config.json -> config.luau
local serde = require("@lune/serde")
local fs = require("@lune/fs")

local cfg = serde.decode("json", fs.readFile("./config.json"))
local size = 0

-- get size of the dictionary
for i, _ in pairs(cfg) do
    size += 1
end

-- add each table, key as raw file contents
local contents = "-- THIS CONFIG IS **AUTO-GENERATED**\n-- PLEASE EDIT config.json INSTEAD!\nreturn {\n"
for i, v in pairs(cfg) do
    local value = v
    if tonumber(v) and not v:find("%.") then
        value = tonumber(v)
    elseif v ~= true and v ~= false then
        v = '"'..tostring(value)..'"'
    end

    contents = contents.."    "..i.." = "..tostring(v)..",\n"
end
contents = contents.."}"

-- write to config.luau
fs.writeFile("./config.luau", contents)

return {}