local serde = require("@lune/serde")
local fs = require("@lune/fs")

local setting_get

setting_get = {

    callback = function(args, options)

        local effect = args[2]
        local key = args[3]

        if effect == nil then
            print("setting_get command must have an effect!")
            return
        end

        if key == nil then
            print("setting_get command must have a key!")
            return
        end

        if not fs.readDir("./effects/"..effect) then
            error(effect.." does not exist.")
        elseif not fs.readFile("./effects/"..effect.."/config.json") then
            error(effect.." does not have a config.json")
        end

        -- json -> table
        local json = serde.decode("json", fs.readFile("./effects/"..effect.."/config.json"))
        if not json then
            error(effect.." could not parse config.json")
        end

        if json[key] == nil then
            error(effect.." does not have settings key " .. key)
        end

        local value = json[key]
        local valueType = tostring(type(json[key]))

        if type(json[key]) == "table" and type(json[key][1]) == "string" and json[key][1]:sub(1,3) == "RGB" then
            valueType = "RGBColor"
            
            value = "("
            local counter = 0
            for i, v in pairs(json[key]) do
                if v == "RGBColor" then continue end
                counter += 1
                if counter == 1 then
                    value = value..v
                    continue
                end
                value = value .. "_" .. v
            end
            value = value .. ")"
        end

        print(tostring(value) .. ": " .. tostring(valueType))
    end,

    description = "Get the current value of a setting",

    -- the arg table contains strings which could be options, or types
    args = {effect = {"effect", "string"}, key = {"key", "string"}},
    argsorder = {"effect", "key"},
    example = "setting_get BouncingBallWithSolidBackground BACKGROUND_COLOR"
}

return setting_get