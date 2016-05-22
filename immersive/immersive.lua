-- IMMERSIVE
local BASEURL = "http://localhost:8000/"
local STEP = 0.5

immersive.colors = "pixels"
immersive.player = false

minetest.register_chatcommand("bindPlayer", {

	params = "",
	description = "Bind player to IMMERSIVE",
	func = function(name, param)

		local player = minetest.get_player_by_name(name)
		if not player then
			return false, "Player not found"
		else
			immersive.player = player
			immersive.step()
			return true, "Player "..immersive.player:get_player_name().." bound"
		end
	end,
})

local http = immersive.http

immersive.httpGET = function(uri,callback)
	-- std lenght for GET is 255 bytes
	http.fetch({
		url = BASEURL..uri,
		timeout = 10,
		post_data = nil, --use GET
		user_agent = "minetest http"
		},
	callback)
end

immersive.ext = function (n)

	if n > 0 then
		return n % 1 >= 0.5 and math.ceil(n) or math.floor(n)
	else
		return n % 1 < 0.5 and math.floor(n) or math.ceil(n)
	end
end

immersive.bresenham = function (x0,y0,x1,y1,z)

	local dx = math.abs(x1 - x0)
	local sx = x0 < x1 and 1 or -1
	local dy = math.abs(y1 - y0)
	local sy = y0 < y1 and 1 or -1
	local err = (dx>dy and dx or -dy)/2
				 
	while true do
		immersive.selectNode(x0,y0,z)

		if x0 == x1 and y0 == y1 then break end
		local e2 = err
		if e2 > -dx then
			err = err - dy
			x0 = x0 + sx
		end
		if e2 < dy then
			err = err + dx
			y0 = y0 + sy
		end
	end
end

immersive.selectNode = function (x,y,z)

	local node = minetest.get_node_or_nil({x=x,y=z,z=y}) -- <-- note the y/z inversion /!\
	if not node or node.name == "air" then
		immersive.colors = immersive.colors.."/202020"
	else
		immersive.colors = immersive.colors.."/"..immersive.nodelist[node.name]
	end
end

immersive.pointsFromAngle = function(xorig,yorig,rad,radius)
				
	local deg = rad * 180 / math.pi
	local x = immersive.ext(math.cos(rad)*radius)
    local y = immersive.ext(math.sin(rad)*radius)
   
    local x0 = xorig + x
    local y0 = yorig + y
    local x1 = xorig - x
    local y1 = yorig - y

    if(deg > 90 and deg <= 270) then
   		x0 = xorig - x
   		y0 = xorig - y
   		x1 = xorig + x
   		y1 = yorig + y
    end

    return {x0=x0,y0=y0,x1=x1,y1=y1}
end

immersive.step = function()
	
	if not immersive.player then return end
	local perf = minetest.get_us_time() -- microseconds
	immersive.colors = "pixels" -- reset color string
	local yawRad = immersive.player:get_look_yaw() - 1.570796327 -- 90 deg offset, see mt doc

	local pos = immersive.player:getpos()
	-- NOTE about coords
	-- immersive uses 2D coords x,y 
	-- yet minetest uses 3D coords  x,y,z (dir x, elevation y, dir z)
	--
	-- To facilitate the usage of x,y,z in this code
	-- I will rename minetest's y-axis as z (elevation)
	-- and minetest's z-axis as y (direction y)
	local x = immersive.ext(pos.x)
	local y = immersive.ext(pos.z)
	local z = math.floor(pos.y)

	local p = immersive.pointsFromAngle(x,y,yawRad,6)
	immersive.bresenham(p.x0,p.y0,p.x1,p.y1,z)
	immersive.httpGET(immersive.colors,function()
		print("++Step completed in "..(minetest.get_us_time()-perf).."us++")
	end)
	minetest.after(STEP,immersive.step)
end

minetest.register_on_player_hpchange(function(player, hp_change)
	if immersive.player and
		player:get_player_name() == immersive.player:get_player_name() and
			hp_change < 0 then
		print("player hurt")
		immersive.httpGET("hurt", function()
			print("player hurt")
		end)
	end
end)

print("Loading nodelist ...")
local file = io.open("tm.json","r")
immersive.nodelist = minetest.parse_json(file:read("*a"))
file:close()
print("Loading nodelist ... done!")
