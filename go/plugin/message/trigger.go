package message

// TriggerStart is the format of the message that starts a Trigger
type TriggerStart struct {
	TriggerID int    `json:"trigger_id"` // TriggerId that identifies the trigger in the system
	Trigger   string `json:"trigger"`    // Trigger is the name of the trigger
	startMessage
}

// TriggerEvent messages encapsulate any output event emitted by the plugins.
type TriggerEvent struct {
	TriggerID int           `json:"trigger_id"`
	Output    OutputMessage `json:"output"`
}
