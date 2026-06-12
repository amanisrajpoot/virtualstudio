extends Node
class_name StoryForgeAssetRegistryClient

signal assets_listed(assets: Array)
signal asset_loaded(asset: Dictionary)
signal asset_validated(result: Dictionary)
signal request_failed(message: String, status_code: int)

@export var base_url: String = "http://127.0.0.1:8000"

var _request: HTTPRequest
var _pending_action: String = ""


func _ready() -> void:
    _request = HTTPRequest.new()
    add_child(_request)
    _request.request_completed.connect(_on_request_completed)


func list_assets(asset_type: String = "", query: String = "", limit: int = 100, offset: int = 0) -> void:
    var params: Array[String] = []
    if asset_type != "":
        params.append("type=%s" % asset_type.uri_encode())
    if query != "":
        params.append("q=%s" % query.uri_encode())
    params.append("limit=%d" % limit)
    params.append("offset=%d" % offset)

    var url := "%s/assets?%s" % [_normalized_base_url(), "&".join(params)]
    _send("list_assets", url, HTTPClient.METHOD_GET)


func get_asset(asset_id: String) -> void:
    var url := "%s/assets/%s" % [_normalized_base_url(), asset_id.uri_encode()]
    _send("get_asset", url, HTTPClient.METHOD_GET)


func validate_asset(asset: Dictionary) -> void:
    var url := "%s/assets/validate" % _normalized_base_url()
    _send("validate_asset", url, HTTPClient.METHOD_POST, asset)


func _send(action: String, url: String, method: int, body: Dictionary = {}) -> void:
    if _request.get_http_client_status() != HTTPClient.STATUS_DISCONNECTED:
        request_failed.emit("asset registry request already in flight", 0)
        return

    _pending_action = action
    var headers := PackedStringArray(["Content-Type: application/json"])
    var payload := "" if body.is_empty() else JSON.stringify(body)
    var error := _request.request(url, headers, method, payload)
    if error != OK:
        _pending_action = ""
        request_failed.emit("failed to start asset registry request", 0)


func _on_request_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
    var text := body.get_string_from_utf8()
    var parsed = null
    if text != "":
        parsed = JSON.parse_string(text)

    if response_code < 200 or response_code >= 300:
        var message := "asset registry request failed"
        if typeof(parsed) == TYPE_DICTIONARY and parsed.has("detail"):
            message = str(parsed["detail"])
        request_failed.emit(message, response_code)
        _pending_action = ""
        return

    match _pending_action:
        "list_assets":
            assets_listed.emit(parsed if typeof(parsed) == TYPE_ARRAY else [])
        "get_asset":
            asset_loaded.emit(parsed if typeof(parsed) == TYPE_DICTIONARY else {})
        "validate_asset":
            asset_validated.emit(parsed if typeof(parsed) == TYPE_DICTIONARY else {})

    _pending_action = ""


func _normalized_base_url() -> String:
    return base_url.trim_suffix("/")
