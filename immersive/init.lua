immersive = {}

immersive.http = minetest.request_http_api()

if not immersive.http then
	minetest.log("error","Http accesss not granted")
else
	local modpath = minetest.get_modpath("immersive")

	dofile( modpath.."/immersive.lua" )
	
	minetest.log("info","immersive is up and running")
end