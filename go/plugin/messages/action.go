package messages

import "encoding/json"

type ActionStart struct {
	// ActionId that identifies the action in the system
	ActionID int `json:"action_id"`
	// Connection is the global connection for the plugin
	Connection json.RawMessage `json:"connection"`
	// Action is the name of the action
	Action string `json:"action"`
	// Input are the input passed to action start
	Input json.RawMessage `json:"input"`
}

type ActionResult struct {
	ActionID int             `json:"action_id"`
	Uid      string          `json:"uid"`
	Status   string          `json:"status"`
	Error    string          `json:"error"`
	Output   json.RawMessage `json:"output"`
}
