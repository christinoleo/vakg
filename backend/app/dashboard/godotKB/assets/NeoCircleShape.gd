tool
extends ConvexPolygonShape2D
class_name NeoCircleShape

export (float) var radius = 1 setget set_radius
export (int) var resolution = 8 setget set_resolution


func set_radius(v):
	if v > 0:
		radius = v
		update()
	
func set_resolution(v):
	if v > 3:
		resolution = v
		update()

func update():
	var p = PoolVector2Array()
	for i in range(resolution):
		var angle := deg2rad(range_lerp(i, 0, resolution, 0, 360))
		p.append(Vector2(radius*cos(angle), radius*sin(angle)))
	set_point_cloud(p)
	
func _init() -> void:
	update()
