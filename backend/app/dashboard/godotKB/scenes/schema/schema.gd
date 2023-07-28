extends Node2D


onready var _result = $gui/drawer/bottom/result
onready var client:HTTPRequest = $HTTPRequest
onready var network = $network
var url = 'http://127.0.0.1:8888/schema'

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	create_network()


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta: float) -> void:
#	pass

func create_network(data: Dictionary = {}):
	var nodes = []
	var edges = []
	var v = 0
	if data.has('nodes'):
		for n in data['nodes']:
			nodes.append(NodeResource.new(str(n['id']), n['labels'][0], Vector2(v,v)))
			v+=50
	if data.has('relationships'):
		for e in data['relationships']:
			edges.append(EdgeResource.new(str(e['id']), e['name'], str(e['source']), str(e['target'])))
	network.set_nodes(nodes)
	network.set_edges(edges)

func _on_HTTPRequest_request_completed(result: int, response_code: int, headers: PoolStringArray, body: PoolByteArray) -> void:
	if response_code != 200:
		push_error("Bad Response code!")
		_result.text = 'Bad Response code! \n Error: ' + body.get_string_from_utf8()
		return
		
	var json = JSON.parse(body.get_string_from_utf8())
	if json.error != OK:
		push_error("An error occurred in the HTTP response.")
		_result.text = "An error occurred in the HTTP response."
		return
	var parsed = json.result
	_result.text = JSON.print(parsed, "\t")
	create_network(parsed)
	prints(result, response_code, headers, parsed)


func _on_query_button_down() -> void:
	_result.text = 'SENDING'
	get_tree().set_input_as_handled()
	var error = client.request(url)
	if error != OK:
		push_error("An error occurred in the HTTP request.")
		_result.text = "An error occurred in the HTTP request."
	_result.text = 'SENT'
