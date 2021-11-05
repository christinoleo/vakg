extends Resource
class_name NodeResource

export var id: String
export var label: String = 'node'
export var position: Vector2 = Vector2.ZERO

func _init(id:String, label:='node', position:=Vector2.ZERO) -> void:
	self.id = id
	self.label = label
	self.position = position
	if id == null: 
		self.id = str(get_instance_id())
