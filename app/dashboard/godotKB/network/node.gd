tool
extends RigidBody2D

signal on_moved(node, pos)
signal on_hover_start(node)
signal on_hover_end(node)

export var text: String = 'node' setget set_text
var _raised := false
var _old_mouse_position := Vector2.ZERO

onready var label = $Label
var camera

func set_text(v):
	text = v
	if text and label:
		$Label.text = str(text)


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	$HoverShape.hide()
	set_text(text)
	set_notify_transform(true)
	set_process(_raised)


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSFORM_CHANGED:
		emit_signal('on_moved', self, global_position)



# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta: float) -> void:
#	pass


func _on_mouse_entered() -> void:
	emit_signal('on_hover_start', self)
	$HoverShape.show()


func _on_mouse_exited() -> void:
	emit_signal('on_hover_end', self)
	$HoverShape.hide()
#	_raised = false
#	set_process(_raised)

func _integrate_forces(state: Physics2DDirectBodyState) -> void:
	rotation = 0
	emit_signal('on_moved', self, global_position)
	

func _process(delta: float) -> void:
	var new_pos = get_viewport().get_mouse_position() * camera.zoom.x
	if _old_mouse_position.distance_to(new_pos) > 2:
		global_position += new_pos-_old_mouse_position
#		move_and_collide((new_pos - _old_mouse_position))
		_old_mouse_position = new_pos
		emit_signal('on_moved', self, new_pos)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == BUTTON_LEFT and not event.pressed:
		_raised = false
		set_process(_raised)
		mode = MODE_RIGID


func _on_input_event(viewport: Node, event: InputEvent, shape_idx: int) -> void:
	if event is InputEventMouseButton:
		if event.button_index == BUTTON_LEFT:
			_raised = event.pressed
			if _raised: mode = MODE_KINEMATIC
			else: mode = MODE_RIGID
			set_process(_raised)
			get_tree().set_input_as_handled()
			_old_mouse_position = get_viewport().get_mouse_position() * camera.zoom.x
	
