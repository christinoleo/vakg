tool
extends Node2D

signal on_connected(edge, source, target)
signal on_disconnected(edge, source, target)

export(NodePath) var source setget set_source
export(NodePath) var target setget set_target
export var text : String = 'test'

export(bool) var update setget _update

onready var label = $Label

var _source
var _target


func set_source(v):
	source = v
	if v: 
		if _source and _target: emit_signal('on_disconnected', self, _source, _target)
		_source = get_node_or_null(source)
		if _source and _target: emit_signal('on_connected', self, _source, _target)
	_update()
	
	
func set_target(v):
	target = v
	if v:
		if _source and _target: emit_signal('on_disconnected', self, _source, _target)
		_target = get_node_or_null(target)
		if _source and _target: emit_signal('on_connected', self, _source, _target)
	_update()
	

func _update(v=null):
	if _source and _target:
#		prints('UPDATE',_source.global_position, _target.global_position)
		label.text = text
		if _source.position.distance_to(_target.position) > 10:
			position = (_source.position+_target.position)/2
			$normaledge.curve.clear_points()
			$normaledge.curve.add_point(_source.position-position)
			$normaledge.curve.add_point(_target.position-position)
		else:
			position = (_source.position+_target.position)/2
			$normaledge.hide()
			$loopedge.show()
			$Label.set_position(Vector2(-213, -243))
		update()
		
# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	$loopedge.hide()
	if target: _target = get_node_or_null(target)
	if source: _source = get_node_or_null(source)
	if _source and _target: 
		emit_signal('on_connected', self, _source, _target)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
