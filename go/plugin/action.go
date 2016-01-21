package plugin

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	uuid "github.com/satori/go.uuid"

	"github.com/orcalabs/plugin-sdk/go/plugin/messages"
)

type Action struct {
	ActionID      int
	DispatcherURL string

	connection interface{}
	input      interface{}
	action     string
}

type ActionVars interface {
	// Connection for the plugin
	Connection() interface{}
	// Name of action
	Name() string
	// Input struct for the action
	Input() interface{}
}

// Init will initialize the action and set all of its internal vars
// to pointers to the implementations of the connection and parameters.
func (act *Action) Init(vars ActionVars) {
	act.connection = vars.Connection()
	act.input = vars.Input()
	act.action = vars.Name()
}

func (act *Action) emit(event interface{}, errMsg string, writer io.Writer) error {
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

	result := messages.ActionResult{ActionID: act.ActionID,
		Uid: uuid.NewV4().String(), Status: status, Error: errMsg, Output: eventBytes}

	jsonStr, err := MarshalMessage("action_result", &result)

	if err != nil {
		return err
	}

	_, err = writer.Write(jsonStr)

	return err
}

// Done will complete the action
func (act *Action) Done(event interface{}) error {
	return act.emit(event, "", os.Stdout)
}

// Error will write the error message
func (act *Action) Failed(err string) error {
	return act.emit(nil, err, os.Stdout)
}

// ReadStart will read the start for the action
func (act *Action) ReadStart() error {
	startMessage := &messages.ActionStart{}
	_, err := UnmarshalMessage("action_start", &startMessage)

	if err != nil {
		return err
	}

	act.ActionID = startMessage.ActionID

	if startMessage.Action != act.action {
		return fmt.Errorf("Expected action %s but got %s", act.action, startMessage.Action)
	}

	err = json.Unmarshal(startMessage.Connection, act.connection)

	if err != nil {
		return fmt.Errorf("Unable to parse connection %s", err)
	}

	err = json.Unmarshal(startMessage.Input, act.input)

	if err != nil {
		return fmt.Errorf("Unable to parse parameters %s", err)
	}

	return nil
}
