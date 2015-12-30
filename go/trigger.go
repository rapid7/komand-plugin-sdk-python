package plugin

import (
	"encoding/json"
	"fmt"

	"github.com/orcalabs/plugin-sdk/go/messages"
)

type Trigger struct {
	DispatcherURL string
	Meta          messages.Meta

	config  interface{}
	params  interface{}
	trigger string
}

type TriggerVars interface {
	// Config for the plugin
	Config() interface{}
	// Name of trigger
	Name() string
	// Parameters struct for the trigger
	Parameters() interface{}
}

// Init will initialize the trigger and set all of its internal vars
// to pointers to the implementations of the config and parameters.
func (tp *Trigger) Init(vars TriggerVars) {
	tp.config = vars.Config()
	tp.params = vars.Parameters()
	tp.trigger = vars.Name()
}

// Send will dispatch a trigger event
func (tp *Trigger) Send(event interface{}) error {
	return DispatchTriggerEvent(tp.DispatcherURL, event, tp.Meta)
}

// ReadStart will read the start for the trigger
func (tp *Trigger) ReadStart() error {
	startMessage := &messages.TriggerStart{}

	msg, err := UnmarshalMessage("trigger_start", &startMessage)

	if err != nil {
		return err
	}

	tp.DispatcherURL = startMessage.DispatcherURL
	tp.Meta = msg.Meta

	if startMessage.Trigger != tp.trigger {
		return fmt.Errorf("Expected trigger %s but got %s", tp.trigger, startMessage.Trigger)
	}

	if tp.DispatcherURL == "" {
		return fmt.Errorf("Expected required dispatcher_url but nothing found: %+v", startMessage)
	}

	err = json.Unmarshal(startMessage.Config, tp.config)

	if err != nil {
		return fmt.Errorf("Unable to parse config %s", err)
	}

	err = json.Unmarshal(startMessage.Parameters, tp.params)

	if err != nil {
		return fmt.Errorf("Unable to parse parameters %s", err)
	}

	return nil

}
