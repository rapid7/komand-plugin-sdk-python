package plugin

import "fmt"

// Actionable is an interface that an Action needs to implement
type Actionable interface {
	Runner
	Connection() interface{} // Connection for the plugin
	Input() interface{}      // Input struct for the action
}

// Action is a
type Action struct {
	ActionID      int
	DispatcherURL string
	Name          string
	connection    interface{}
	input         interface{}
}

// Connection returns the connection for the Action
func (a Action) Connection() interface{} {
	return &a.connection
}

// Input returns the input for the Action
func (a Action) Input() interface{} {
	return &a.input
}

// Run must be implemented by the Plugin Action
func (a Action) Run() error {
	return fmt.Errorf("Run action failed: Run() method not implemented")
}
