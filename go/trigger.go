package plugin

import (
	"encoding/json"
	"fmt"

	"github.com/orcalabs/plugin-sdk/go/messages"
)

type Trigger struct {
	TriggerID     int
	DispatcherURL string

	connection interface{}
	input      interface{}
	trigger    string
}

type TriggerVars interface {
	// Connection for the plugin
	Connection() interface{}
	// Name of trigger
	Name() string
	// Input struct for the trigger
	Input() interface{}
}

// Init will initialize the trigger and set all of its internal vars
// to pointers to the implementations of the connection and input.
func (tp *Trigger) Init(vars TriggerVars) {
	tp.connection = vars.Connection()
	tp.input = vars.Input()
	tp.trigger = vars.Name()
}

// Send will dispatch a trigger event
func (tp *Trigger) Send(event interface{}) error {
	return DispatchTriggerEvent(tp.DispatcherURL, event)
}

// ReadStart will read the start for the trigger
func (tp *Trigger) ReadStart() error {
	startMessage := &messages.TriggerStart{}
	_, err := UnmarshalMessage("trigger_start", &startMessage)

	if err != nil {
		return err
	}

	tp.TriggerID = startMessage.TriggerID
	tp.DispatcherURL = startMessage.DispatcherURL

	if startMessage.Trigger != tp.trigger {
		return fmt.Errorf("Expected trigger %s but got %s", tp.trigger, startMessage.Trigger)
	}

	if tp.DispatcherURL == "" {
		return fmt.Errorf("Expected required dispatcher_url but nothing found: %+v", startMessage)
	}

	err = json.Unmarshal(startMessage.Connection, tp.connection)

	if err != nil {
		return fmt.Errorf("Unable to parse connection %s", err)
	}

	err = json.Unmarshal(startMessage.Input, tp.input)

	if err != nil {
		return fmt.Errorf("Unable to parse input %s", err)
	}

	return nil

}
