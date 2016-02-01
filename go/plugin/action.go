package plugin

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
	"github.com/satori/go.uuid"
)

// Actionable is an interface that an Action needs to implement
type Actionable interface {
	Runner
	Name() string            // Name for the plugin
	Connection() interface{} // Connection for the plugin
	Input() interface{}      // Input struct for the action
}

// Action is a
type Action struct {
	ActionID      int
	DispatcherURL string
	name          string
	connection    interface{}
	input         interface{}
}

// Name returns the name for the Action
func (a Action) Name() string {
	return a.name
}

// Connection returns the connection for the Action
func (a Action) Connection() interface{} {
	return &a.connection
}

// Input returns the input for the Action
func (a Action) Input() interface{} {
	return &a.input
}

// Init will initialize the action and set all of its internal vars
// to pointers to the implementations of the connection and parameters.
func (a *Action) Init(ac Actionable) {
	a.connection = ac.Connection()
	a.input = ac.Input()
	a.name = ac.Name()
}

// Run must be implemented by the Plugin Action
func (a Action) Run() error {
	return a.ReadStartMessage()
}

// ReadStartMessage will read the start for the action
func (a *Action) ReadStartMessage() error {
	startMessage := &message.ActionStart{}

	_, err := UnmarshalMessage("action_start", &startMessage)
	if err != nil {
		return err
	}

	a.ActionID = startMessage.ActionID

	if startMessage.Action != a.Name() {
		return fmt.Errorf("Expected action %s but got %s", a.Name(), startMessage.Action)
	}

	err = json.Unmarshal(startMessage.Connection, a.connection)
	if err != nil {
		return fmt.Errorf("Unable to parse connection %s", err)
	}

	err = json.Unmarshal(startMessage.Input, a.input)
	if err != nil {
		return fmt.Errorf("Unable to parse parameters %s", err)
	}

	return nil
}

// Done will complete the action
func (a Action) Done(event interface{}) error {
	return a.emit(event, "", os.Stdout)
}

// Failed will write the error message
func (a Action) Failed(err string) error {
	return a.emit(nil, err, os.Stdout)
}

// Emit emits events from the Action
func (a Action) emit(event interface{}, errMsg string, writer io.Writer) error {
	var eventBytes = []byte("")
	var err error

	if event != nil {
		eventBytes, err = json.Marshal(event)

		if err != nil {
			return err
		}
	}

	status := "ok"

	if errMsg != "" {
		status = "error"
	}

	result := message.ActionResult{
		ActionID: a.ActionID,
		Status:   status,
		Error:    errMsg,
	}
	result.Output = eventBytes
	result.UID = uuid.NewV4().String()

	jsonStr, err := MarshalMessage("action_result", &result)
	if err != nil {
		return err
	}

	_, err = writer.Write(jsonStr)
	return err
}
