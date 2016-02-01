package plugin

import (
	"encoding/json"
	"fmt"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
)

// Triggerable is an interface that any Trigger must implement
type Triggerable interface {
	Runner
	Name() string            // Name for the trigger
	Connection() interface{} // Connection for the trigger
	Input() interface{}      // Input for the trigger
}

// Trigger defines a struct that can be embedded within any implemented Trigger
type Trigger struct {
	ID            int
	DispatcherURL string

	name       string
	connection interface{}
	input      interface{}
}

// Name returns the name of the Trigger
func (t Trigger) Name() string {
	return t.name
}

// Connection returns the connection for the Trigger
func (t Trigger) Connection() interface{} {
	return &t.connection
}

// Input returns the input for the Trigger
func (t Trigger) Input() interface{} {
	return &t.input
}

// Init will initialize the trigger and set all of its internal vars
// to pointers to the implementations of the connection and input
func (t *Trigger) Init(tr Triggerable) {
	t.name = tr.Name()
	t.connection = tr.Connection()
	t.input = tr.Input()
}

// Send will dispatch a trigger event
func (t *Trigger) Send(event interface{}) error {
	return DispatchTriggerEvent(t.DispatcherURL, event)
}

// Run returns the default run behavior for the Trigger
func (t Trigger) Run() error {
	return t.ReadStartMessage()
}

// ReadStartMessage reads the start message for the trigger
func (t Trigger) ReadStartMessage() error {
	startMessage := message.TriggerStart{}
	_, err := UnmarshalMessage("trigger_start", &startMessage)
	if err != nil {
		return err
	}

	t.ID = startMessage.TriggerID
	t.DispatcherURL = startMessage.DispatcherURL

	if startMessage.Trigger != t.name {
		return fmt.Errorf("Expected trigger %s but got %s", t.name, startMessage.Trigger)
	}

	if t.DispatcherURL == "" {
		return fmt.Errorf("Expected required dispatcher_url but none found: %+v", startMessage)
	}

	err = json.Unmarshal(startMessage.Connection, t.connection)
	if err != nil {
		return fmt.Errorf("Unable to parse connection %s", err)
	}

	err = json.Unmarshal(startMessage.Input, t.input)
	if err != nil {
		return fmt.Errorf("Unable to parse input %s", err)
	}

	return nil
}
