package message

import "github.com/orcalabs/plugin-sdk/go/plugin/connect"

// ActionStart is the format of the message that starts an Action
type ActionStart struct {
	ActionID   int                `json:"action_id"`  // ActionId identifies the action in the system
	Action     string             `json:"action"`     // Action is the name of the action
	Connection connect.Connection `json:"connection"` // Connection is the global connection for the plugin
	Input      Input              `json:"input"`      // Input are the input passed to action start
}

// ActionResult is the format of the message from an Actions result
type ActionResult struct {
	ActionID int    `json:"action_id"` // ActionId identifies the action in the system
	Status   string `json:"status"`    // Status identifies the result status from the Action
	Error    string `json:"error"`     // Error identifies any error that occured during the Action
	Output   Output `json:"output"`    // Output contains the output of the Action
}
