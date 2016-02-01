package message

import (
	"encoding/json"

	"github.com/satori/go.uuid"
)

// TriggerStart is the format of the message that starts a Trigger
type TriggerStart struct {
	Message
	TriggerID     int             `json:"trigger_id"`     // TriggerId that identifies the trigger in the system
	Connection    json.RawMessage `json:"connection"`     // Connection is the global connection for the plugin
	DispatcherURL string          `json:"dispatcher_url"` // Dispatcher URL is the url for the channel
	Trigger       string          `json:"trigger"`        // Trigger is the name of the trigger
	Input         Input           `json:"input"`          // Input are the parameters passed to trigger start
}

// Init initializes a TriggerStart message
func (m *TriggerStart) Init() error {
	m.UID = uuid.NewV4().String()
	m.Type = "trigger_start"
	m.Version = Version
	return nil
}

// TriggerEvent is the format of the event message that a Trigger emits
// TODO: make this match the models
type TriggerEvent struct {
	Message
	TriggerID int    `json:"trigger_id"`
	Output    Output `json:"output"`
}

// Init initializes a TriggerEvent message
func (m *TriggerEvent) Init() error {
	m.UID = uuid.NewV4().String()
	m.Type = "trigger_event"
	m.Version = Version
	return nil
}
