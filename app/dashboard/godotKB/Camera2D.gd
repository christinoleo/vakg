extends Camera2D


var _raised:= false
var _origin_mouse:=Vector2.ZERO

func _unhandled_input(event: InputEvent) -> void:
	if Input.is_action_just_released('zoom_out') and zoom.x < 10 and zoom.y < 10:
		zoom.x += 0.25
		zoom.y += 0.25
	if Input.is_action_just_released('zoom_in') and zoom.x > 1 and zoom.y > 1:
		zoom.x -= 0.25
		zoom.y -= 0.25
	if Input.is_action_just_pressed('pan'):
		_raised = true
		_origin_mouse = get_viewport().get_mouse_position()
	elif Input.is_action_just_released('pan'):
		_raised = false

func _process(delta: float) -> void:
	if _raised:
		var new_pos = get_viewport().get_mouse_position()
		global_translate((_origin_mouse - new_pos) * zoom.x)
		_origin_mouse = new_pos

