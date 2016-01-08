package messages

import "encoding/json"

type TriggerStart struct {
	// TriggerId that identifies the trigger in the system
	TriggerID int `json:"trigger_id"`
	// Config is the global config for the plugin
	Config json.RawMessage `json:"config"`
	// Dispatcher URL is the url for the channel
	DispatcherURL string `json:"dispatcher_url"`
	// Trigger is the name of the trigger
	Trigger string `json:"trigger"`
	// Parameters are the parameters passed to trigger star
	Parameters json.RawMessage `json:"parameters"`
}

// TODO: make this match the models
type TriggerEvent struct {
	TriggerID int             `json:"trigger_id"`
	Uid       string          `json:"uid"`
	Event     json.RawMessage `json:"event"`
}
