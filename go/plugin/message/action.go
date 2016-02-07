package message

// ActionStart is the format of the message that starts an Action
type ActionStart struct {
	ActionID int    `json:"action_id"` // ActionId identifies the action in the system
	Action   string `json:"action"`    // Action is the name of the action
	startMessage
}

// ActionResult is the format of the message from an Actions result
type ActionResult struct {
	ActionID int           `json:"action_id"` // ActionId identifies the action in the system
	Status   string        `json:"status"`    // Status identifies the result status from the Action
	Error    string        `json:"error"`     // Error identifies any error that occured during the Action
	Output   OutputMessage `json:"output"`    // Output contains the output of the Action
}
