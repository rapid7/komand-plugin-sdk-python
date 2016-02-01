package message

import "encoding/json"

// TriggerStart is the format of the message that starts a Trigger
type TriggerStart struct {
	UID           string          `json:"uid"`
	TriggerID     int             `json:"trigger_id"`     // TriggerId that identifies the trigger in the system
	Connection    json.RawMessage `json:"connection"`     // Connection is the global connection for the plugin
	DispatcherURL string          `json:"dispatcher_url"` // Dispatcher URL is the url for the channel
	Trigger       string          `json:"trigger"`        // Trigger is the name of the trigger
	Input         json.RawMessage `json:"input"`          // Input are the parameters passed to trigger start
}

// TriggerEvent is the format of the event message that a Trigger emits
// TODO: make this match the models
type TriggerEvent struct {
	UID       string          `json:"uid"`
	TriggerID int             `json:"trigger_id"`
	Output    json.RawMessage `json:"output"`
}
