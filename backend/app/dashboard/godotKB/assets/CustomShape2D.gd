tool
extends Node2D


export var shape: Shape2D setget set_shape_2d
export var color: Color = Color.white setget set_color


func set_shape_2d(v):
	if shape != null:
		shape.disconnect('changed', self, 'update')
	shape = v
	update()
	if shape != null:
		shape.connect('changed', self, 'update')
		
func set_color(v):
	color = v
	update()


func _draw() -> void:
	if shape != null:
		shape.draw(get_canvas_item(), color)
	

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	update()


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta: float) -> void:
#	pass
