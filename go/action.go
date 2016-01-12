package plugin

import (
	"encoding/json"
	"fmt"
	uuid "github.com/satori/go.uuid"
	"io"
	"os"

	"github.com/orcalabs/plugin-sdk/go/messages"
)

type Action struct {
	ActionID      int
	DispatcherURL string

	config interface{}
	params interface{}
	action string
}

type ActionVars interface {
	// Config for the plugin
	Config() interface{}
	// Name of action
	Name() string
	// Parameters struct for the action
	Parameters() interface{}
}

// Init will initialize the action and set all of its internal vars
// to pointers to the implementations of the config and parameters.
func (act *Action) Init(vars ActionVars) {
	act.config = vars.Config()
	act.params = vars.Parameters()
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

	err = json.Unmarshal(startMessage.Config, act.config)

	if err != nil {
		return fmt.Errorf("Unable to parse config %s", err)
	}

	err = json.Unmarshal(startMessage.Parameters, act.params)

	if err != nil {
		return fmt.Errorf("Unable to parse parameters %s", err)
	}

	return nil
}
