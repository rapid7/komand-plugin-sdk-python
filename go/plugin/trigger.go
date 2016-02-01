package plugin

import (
	"encoding/json"
	"fmt"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
)

// Triggerable is an interface that any Trigger must implement
type Triggerable interface {
	Runner
	Connection() *Connection // Connection for the trigger
	Input() *message.Input   // Input for the trigger
}

// Trigger defines a struct that can be embedded within any implemented Trigger
type Trigger struct {
	ID            int
	DispatcherURL string
	Name          string
	connection    Connection
	input         message.Input
}

// Connection returns the connection for the Trigger
func (t Trigger) Connection() *Connection {
	return &t.connection
}

// Input returns the input for the Trigger
func (t Trigger) Input() *message.Input {
	return &t.input
}

// Run returns the default run behavior for the Trigger
func (t Trigger) Run() error {
	return t.ReadStartMessage()
}

// ReadStartMessage reads the start message for the trigger
func (t Trigger) ReadStartMessage() error {
	startMessage := message.TriggerStart{}
	startMessage.Init()

	_, err := startMessage.Unmarshal()
	if err != nil {
		return err
	}

	t.ID = startMessage.TriggerID
	t.DispatcherURL = startMessage.DispatcherURL

	if startMessage.Trigger != t.Name {
		return fmt.Errorf("Expected trigger %s but got %s", t.Name, startMessage.Trigger)
	}

	if t.DispatcherURL == "" {
		return fmt.Errorf("Expected required dispatcher_url but nothing found: %+v", startMessage)
	}

	err = json.Unmarshal(startMessage.Connection, t.connection)
	if err != nil {
		return fmt.Errorf("Unable to parse connection %s", err)
	}

	err = json.Unmarshal(startMessage.Input.RawMessage, t.input)
	if err != nil {
		return fmt.Errorf("Unable to parse input %s", err)
	}

	return nil
}
