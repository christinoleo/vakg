tool
extends Node2D

var i_edge = preload("res://network/edge.tscn")
var i_node = preload("res://network/node.tscn")

export(NodePath) var camera
export var nodes = []
export var edges = []
export(bool) var update_b setget _reload

var edge_cache : Dictionary = {}
var node_cache: Dictionary = {}

func set_nodes(v):
	nodes = v
	_reload()

func set_edges(v):
	edges = v
	_reload()
	
func _reload(v=null):
	for c in $edges.get_children(): c.free()
	for c in $nodes.get_children(): c.free()
	edge_cache.clear()
	
	for n in nodes:
		var _n = i_node.instance()
		_n.camera = get_node(camera)
		_n.name = n.id
		_n.text = n.label
		_n.position = n.position
		node_cache[n.id] = _n
		$nodes.add_child(_n)
		_n.set_owner($nodes)
		_n.connect('on_moved', self, '_on_node_on_moved')
	
	for e in edges:
		var _e = i_edge.instance()
		_e.name = e.id
		_e.text = e.label
		$edges.add_child(_e)
		_e.set_owner($edges)
		_e.source = get_path_to(node_cache[e.source_id])
		_e._source = node_cache[e.source_id]
		_e.target = get_path_to(node_cache[e.target_id])
		_e._target = node_cache[e.target_id]
		if not edge_cache.has(_e._source): edge_cache[_e._source] = []
		if not edge_cache.has(_e._target): edge_cache[_e._target] = []
		edge_cache[_e._source].append({'source': _e._source, 'target': _e._target, 'edge': _e})
		edge_cache[_e._target].append({'source': _e._source, 'target': _e._target, 'edge': _e})
		_e._update()
		_e.connect('on_connected', self, '_on_edge_on_connected')
		_e.connect('on_disconnected', self, '_on_edge_on_disconnected')

# Called when the node enters the scene tree for the first time.
#func _ready() -> void:
#	for e in $edges.get_children():
#		e.emit_connected()


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta: float) -> void:
#	pass

func _get_configuration_warning():
	if not camera:
		return 'Camera not set'
	return ''

func _on_node_on_moved(node, pos) -> void:
	if edge_cache.has(node): 
		for e in edge_cache[node]:
			e['edge']._update()


func _on_edge_on_connected(edge, source, target) -> void:
	if not edge_cache.has(source): edge_cache[source] = []
	if not edge_cache.has(target): edge_cache[target] = []
	edge_cache[source].append({'source': source, 'target': target, 'edge': edge})
	edge_cache[target].append({'source': source, 'target': target, 'edge': edge})


func _on_edge_on_disconnected(edge, source, target) -> void:
	for e in edge_cache[source]:
		if e['target'] == target: edge_cache[source].erase(e)
	for e in edge_cache[target]:
		if e['source'] == source: edge_cache[target].erase(e)

