package messages

import "encoding/json"

type TriggerStart struct {
	// TriggerId that identifies the trigger in the system
	TriggerID int `json:"trigger_id"`
	// Connection is the global connection for the plugin
	Connection json.RawMessage `json:"connection"`
	// Dispatcher URL is the url for the channel
	DispatcherURL string `json:"dispatcher_url"`
	// Trigger is the name of the trigger
	Trigger string `json:"trigger"`
	// Input are the parameters passed to trigger star
	Input json.RawMessage `json:"input"`
}

// TODO: make this match the models
type TriggerEvent struct {
	TriggerID int             `json:"trigger_id"`
	Uid       string          `json:"uid"`
	Output    json.RawMessage `json:"output"`
}
