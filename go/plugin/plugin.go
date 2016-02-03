package plugin

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"

	"github.com/orcalabs/plugin-sdk/go/plugin/connect"
	"github.com/orcalabs/plugin-sdk/go/plugin/message"
	"github.com/orcalabs/plugin-sdk/go/plugin/parameter"
)

// Types of Start Messages
const (
	TriggerStart = "trigger_start"
	ActionStart  = "action_start"
)

// init initializes the plugin package, collecting parameters from the command line
// Functionality comes from param.go
func init() {
	// defaults to stdin
	parameter.Stdin = parameter.NewParamSet(os.Stdin)

	// check for params after the double dash
	// in the command string
	for i, argv := range os.Args {
		if argv == "--" {
			arg := os.Args[i+1]
			buf := bytes.NewBufferString(arg)
			parameter.Stdin = parameter.NewParamSet(buf)
			break
		}
	}
}

// Pluginable is the interface all Plugins must implement
type Pluginable interface {
	Run() error
	Connect(c connect.Connectable) error
	Trigger(t Triggerable) error
	Act(a Actionable) error
}

// Plugin holds the common Plugin information
type Plugin struct {
	Name       string
	connection connect.Connectable
	triggers   map[string]Triggerable
	actions    map[string]Actionable
}

// Init initializes a Plugin
func (p *Plugin) Init() {
	p.triggers = map[string]Triggerable{}
	p.actions = map[string]Actionable{}
}

// Run runs a Plugin
func (p Plugin) Run() error {
	var typ string
	var version string
	m := message.Message{}
	b := m.Body

	parameter.Param("type", &typ)
	parameter.Param("version", &version)
	parameter.Param("body", &b)
	parameter.Parse()

	var err error
	switch string(typ) {
	case TriggerStart:
		start := message.TriggerStart{}
		json.Unmarshal(b.RawMessage, &start)
		err = p.Trigger(start.Trigger)
	case ActionStart:
		start := message.ActionStart{}
		fmt.Println(string(b.RawMessage))
		json.Unmarshal(b.RawMessage, &start)
		err = p.Act(start.Action)
	}
	return err
}

// Connect connects a Plugin to its connection.  This should be implemented by Plugin developers.
func (p Plugin) Connect() error {
	return errors.New("Failed to connect: Connect() not implemented.")
}

// AddTrigger adds triggers to the map of Plugins triggers
func (p Plugin) AddTrigger(name string, trigger Triggerable) {
	p.triggers[name] = trigger
}

// Trigger triggers on the given trigger if it exists
func (p Plugin) Trigger(trigger string) error {
	if t, ok := p.triggers[trigger]; ok {
		return t.Trigger()
	}
	return fmt.Errorf("Failed to Trigger() with %s. Trigger not valid with plugin: %s.", trigger, p.Name)
}

// Triggers returns the map of Triggerables in the Plugin
func (p Plugin) Triggers() map[string]Triggerable {
	return p.triggers
}

// AddAction adds triggers to the map of Plugins triggers
func (p Plugin) AddAction(name string, action Actionable) {
	p.actions[name] = action
}

// Act acts on the given action if it exists
func (p Plugin) Act(action string) error {
	if a, ok := p.actions[action]; !ok {
		return a.Act()
	}
	return fmt.Errorf("Failed to Act() with action: %s. Action not valid with plugin: %s.", action, p.Name)
}

// Actions returns the map of Actionables in the Plugin
func (p Plugin) Actions() map[string]Actionable {
	return p.actions
}
