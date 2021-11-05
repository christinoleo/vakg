extends Node2D


onready var network = $network


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var nodes = [
		NodeResource.new('node1', 'node1', Vector2(0,0)),
		NodeResource.new('node2', 'node2', Vector2(500,0)),
		NodeResource.new('node3', 'node3', Vector2(500,500)),
		NodeResource.new('node4', 'node4', Vector2(550,550)),
	]
	var edges = [
		EdgeResource.new('edge1', 'edge1', 'node1', 'node3'),
		EdgeResource.new('edge2', 'edge2', 'node1', 'node2'),
		EdgeResource.new('edge3', 'edge3', 'node1', 'node1'),
		EdgeResource.new('edge4', 'edge4', 'node2', 'node2'),
		EdgeResource.new('edge5', 'edge5', 'node3', 'node3'),
		EdgeResource.new('edge6', 'edge6', 'node4', 'node4'),
	]
	network.set_nodes(nodes)
	network.set_edges(edges)

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta: float) -> void:
#	pass
