tool
extends Path2D

export var _curve: Curve2D setget set__curve
var line: Line2D

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if _curve:
		_curve.connect('changed', self, 'update')


func set__curve(value):
	if _curve:
		_curve.disconnect('changed', self, 'update')
	set_curve(value)
	_curve = value
	if value:
		value.connect('changed', self, 'update')
	update()


func update():
	if not line:
		line = get_node_or_null('line')
	if line:
		if _curve:
			line.points = _curve.get_baked_points()
		else:
			line.points = PoolVector2Array()
