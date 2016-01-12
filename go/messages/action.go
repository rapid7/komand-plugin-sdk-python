package messages

import "encoding/json"

type ActionStart struct {
	// ActionId that identifies the action in the system
	ActionID int `json:"action_id"`
	// Config is the global config for the plugin
	Config json.RawMessage `json:"config"`
	// Action is the name of the action
	Action string `json:"action"`
	// Parameters are the parameters passed to action start
	Parameters json.RawMessage `json:"parameters"`
}

type ActionResult struct {
	ActionID int             `json:"action_id"`
	Uid      string          `json:"uid"`
	Status   string          `json:"status"`
	Error    string          `json:"error"`
	Output   json.RawMessage `json:"output"`
}
