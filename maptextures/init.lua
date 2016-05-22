
minetest.log("action","Start mapping textures");

local function getHex(path)
	local f = io.popen("convert "..path.." -scale 1x1 txt:- | grep -Po '#\\w{6}'","r")
	local output = f:read() or "#000000"
	output = string.sub(output , 2) -- remove '#'
	f:close()

	print( output )
	return output

end

local t = {}
for nodename,def in pairs(minetest.registered_nodes) do
	minetest.log("action","Processing "..nodename)
	if def.tiles and def.tiles[1] then
		if def.tiles[1].name then
			toptexture = string.split(def.tiles[1].name,"^")[1]
		else
			toptexture = string.split(def.tiles[1],"^")[1]
		end

		local modname = string.split(nodename,":")[1]
		path = minetest.get_modpath(modname).."/textures/"..toptexture

		t[nodename] = getHex(path)
	end
end
local j = minetest.write_json(t)
local file = io.open("tm.json","w")
file:write(j)
file:close()

minetest.log("action","mapping done")
