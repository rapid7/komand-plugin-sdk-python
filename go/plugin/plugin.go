package plugin

import "fmt"

// Connector is an interface that a type must satisfy if it wants to create a connection within a Plugin
type Connector interface {
	Connect() error
}

// Runner is an interface that a Plugin must satisfy if it wants to run
type Runner interface {
	Run() error
}

// Tester is an interface that a type must satisfy if it wants to be testable within a Plugin
type Tester interface {
	Test() error
}

// Processor is an interface that a type must satisfy if it wants to process within a Plugin
type Processor interface {
	Process() error
}

// Pluginable is an interface that all plugins should implemented
type Pluginable interface {
	Connector
	Tester
}

// Plugin provides a piece of functionality to a workflow.
// When developing a new plugin, this struct should be embedded within it.
type Plugin struct {
	PluginID int
	Name     string
	triggers map[string]Trigger
	actions  map[string]Action
}

// New creates a new instance of a Plugin
func New(name string) (*Plugin, error) {
	return &Plugin{
		Name: name,
	}, nil
}

// Connect connects the Plugin
func (p *Plugin) Connect() error {
	return fmt.Errorf("Failed to connect: Connect() method not implemented.")
}

// Run runs the Plugin
func (p *Plugin) Run() error {
	return fmt.Errorf("Failed to run: Run() method not implemented.")
}

// Test tests the Plugin
func (p *Plugin) Test() error {
	return fmt.Errorf("Failed to test: Test() method not implemented.")
}

// Triggers returns the Triggers for a Plugin
func (p *Plugin) Triggers() map[string]Trigger {
	return p.triggers
}

// Trigger tries to retrieve the Trigger from the Plugin's list of Triggers
// If the Trigger exists, it will return the Trigger and a boolean true
// If the Trigger does not exist, it will return nil and a boolean false
func (p *Plugin) Trigger(trigger string) (Triggerable, bool) {
	if t, ok := p.triggers[trigger]; ok {
		return t, ok
	}
	return nil, false
}

// Actions returns the Actions for a Plugin
func (p *Plugin) Actions() map[string]Action {
	return p.actions
}

// Action tries to retrieve the Action from the Plugin's list of Actions
// If the Action exists, it will return the Action and a boolean true
// If the Action does not exist, it will return nil and a boolean false
func (p *Plugin) Action(action string) (Actionable, bool) {
	if t, ok := p.actions[action]; ok {
		return t, ok
	}
	return nil, false
}
