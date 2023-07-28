extends Resource
class_name EdgeResource

enum Arrows {
	none,
	vee
}

export var id: String
export var label: String
export var source_id: String
export var target_id: String
export var source_arrow := 0
export var target_arrow := 0

func _init(id:String, label:String, source_id: String, target_id: String, source_arrow:=0, target_arrow:=0) -> void:
	self.id = id
	self.label = label
	self.source_id = source_id
	self.target_id = target_id
	self.source_arrow = source_arrow
	self.target_arrow = target_arrow
