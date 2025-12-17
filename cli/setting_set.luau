local serde = require("@lune/serde")
local fs = require("@lune/fs")

local setting_set

setting_set = {

    callback = function(args, options)

        local effect = args[2]
        local key = args[3]
        local value = args[4]

        if effect == nil then
            print("setting_set command must have an effect!")
            return
        end

        if key == nil then
            print("setting_set command must have a key!")
            return
        end

        if value == nil and not options["n"] then
            print("setting_set command must have a value!")
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

        -- type check
        if value:len() >= 3 and value:sub(1, 3) == "RGB" then
            local nottbl = type(json[key]) ~= "table"
            local notstr = type(json[key][1]) ~= "string"
            local notrgb = json[key][1]:sub(1,3) ~= "RGB"
            if nottbl or notstr or notrgb then
                error(effect.." setting " .. key .. " does not match type of " .. value .. "\nJson Value: " .. tostring(type(json[key])) .. "\nNew Value: RGBColor")
            end
            local colors = {}
            for i, v in string.split(value, "_") do
                if v ~= "RGB" then
                    if not tonumber(v) then
                        error(effect.." error setting RGBColor value. Value " .. tostring(v) .. " is not a number.")
                    end
                    table.insert(colors, tonumber(v))
                end
            end
            if #colors ~= 3 then
                error(effect.." error setting RGBColor value. RGBColor value does not have 3 numbers.")
            end
            value = {"RGBColor", colors[1], colors[2], colors[3]}
        elseif type(json[key]) == "table" and type(json[key][1]) == "string" and json[key][1]:len() >= 3 and json[key][1]:sub(1,3) == "RGB" then
            error(effect.." setting " .. key .. " does not match type of " .. value .. "\nJson Value: RGBColor" .. "\nNew Value: " .. tostring(type(value)))
        else

            if value == "true" then
                value = true
            elseif value == "false" then
                value = false
            elseif tonumber(value) then
                value = tonumber(value)
            end
            
            if type(json[key]) ~= type(value) then
                error(effect.." setting " .. key .. " does not match type of " .. tostring(value) .. "\nJson Value: " .. tostring(type(json[key])) .. "\nNew Value: " .. tostring(type(value)))
            end
        end

        json[key] = value

        local newContent = serde.encode("json", json, true)
        fs.writeFile("./effects/"..effect.."/config.json", newContent)
        print(effect.." set setting " .. key .. " to " .. tostring(value))
    end,

    description = "Change a setting in the effects config",

    -- the arg table contains strings which could be options, or types
    args = {effect = {"effect", "string"}, key = {"key", "string"}, value = {"value", "any"}},
    argsorder = {"effect", "key", "value"},
    example = "setting_set BouncingBallWithSolidBackground BACKGROUND_COLOR RGB_255_0_1 ; setting_set BouncingBallWithSolidBackground ENABLE_SOMETHING true ; setting_set BouncingBallWithSolidBackground GRAVITY 20"
}

return setting_set