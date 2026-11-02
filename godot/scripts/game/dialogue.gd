extends Node

# Villager replies from the dialogue model on Modal (dialogue/serve.py). One kept-alive connection, so
# only the first request after a quiet spell pays for the TLS handshake; warm() opens it and wakes the
# server when a village comes near. A failed or slow request answers "" and the villager falls back
# to a scripted line.
const URL := "https://alaiy--village-dialogue-villager-talk.us-east.modal.run"
const TIMEOUT := 8.0
const BROKEN := [HTTPClient.STATUS_DISCONNECTED, HTTPClient.STATUS_CANT_RESOLVE, HTTPClient.STATUS_CANT_CONNECT, HTTPClient.STATUS_CONNECTION_ERROR, HTTPClient.STATUS_TLS_HANDSHAKE_ERROR]

var client := HTTPClient.new()
var queue := []
var current := {}
var sent := false
var age := 0.0
var body := PackedByteArray()


func warm() -> void:
	ask({"warm": true}, func(_reply): pass)


# done(reply) is called once, with "" when there is no answer.
func ask(request: Dictionary, done: Callable) -> void:
	queue.append({"request": request, "done": done})


func _process(dt: float) -> void:
	client.poll()
	var status := client.get_status()
	if current:
		age += dt
		if age > TIMEOUT:
			client.close()
			finish("")
			return
	if status in BROKEN:
		if sent:
			finish("")
		if queue or current:
			client.connect_to_host(URL)
	elif status == HTTPClient.STATUS_BODY:
		body.append_array(client.read_response_body_chunk())
	elif status == HTTPClient.STATUS_CONNECTED:
		if sent:
			var reply = JSON.parse_string(body.get_string_from_utf8())
			finish(reply.get("reply", "") if reply is Dictionary else "")
		elif current or queue:
			if not current:
				current = queue.pop_front()
				age = 0.0
			body.clear()
			sent = client.request(HTTPClient.METHOD_POST, "/", ["Content-Type: application/json"], JSON.stringify(current.request)) == OK


func finish(reply: String) -> void:
	var done: Callable = current.done
	current = {}
	sent = false
	if done.is_valid():
		done.call(reply)
