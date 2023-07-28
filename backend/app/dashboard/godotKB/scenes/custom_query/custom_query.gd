extends Node2D


onready var _query = $gui/drawer/bottom/query
onready var _result = $gui/drawer/bottom/result
onready var client:HTTPRequest = $HTTPRequest

var url = 'http://127.0.0.1:8888/custom_query'


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta: float) -> void:
#	pass

func _input(event: InputEvent) -> void:
	if Input.is_action_just_pressed('execute_query'):
		_result.text = 'SENDING'
		get_tree().set_input_as_handled()
		var body = {'main_request': _query.text, 'variables': []}
		var error = client.request(
			url, 
			[], 
			true,
			HTTPClient.METHOD_POST, 
			JSON.print(body)
		)
		if error != OK:
			push_error("An error occurred in the HTTP request.")
			_result.text = "An error occurred in the HTTP request."
		_result.text = 'SENT'


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
	prints(result, response_code, headers, parsed)
