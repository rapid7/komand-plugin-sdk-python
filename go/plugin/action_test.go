package plugin

import (
	"strings"
	"testing"

	"github.com/komand/plugin-sdk/go/plugin/parameter"
)

var actionStartMessage = `
{
  "version": "v1",
  "type": "action_start",
  "body": {
  	"meta": {
		"action_id": 14
  	},
	"action": "hello_action",
	"connection": { "thing": "one"},
    "input": { "person": "Bob"}
  }
}
`

var invalidTypeActionStartMessage = `
{
  "version": "v1",
  "type": "not_action_start",
  "body": {
  	"meta": {
		"action_id": 14
  	},
    "action": "hello_action",
    "connection": { "thing": "one"},
    "input": { "person": "Bob"}
  }
}
`

type HelloAction struct {
	Action
	output     HelloActionOutput
	input      HelloInput
	connection HelloConnection
}

func (h *HelloAction) Name() string {
	return "hello_action"
}

func (h *HelloAction) Description() string {
	return "hello_action description"
}

func (h *HelloAction) Input() Input {
	return &h.input
}

func (h *HelloAction) Connection() Connection {
	return &h.connection
}

func (h *HelloAction) Output() Output {
	return &h.output
}

type HelloActionOutput struct {
	Greeting string `json:"greeting"`
}

// Validate
func (h *HelloActionOutput) Validate() []error {
	return nil
}

type HelloActionInput struct {
	Person string `json:"person"`
}

// Validate
func (h *HelloActionInput) Validate() []error {
	return nil
}

// Act
func (h *HelloAction) Act() error {
	h.output.Greeting = "good day to you"
	return nil
}

func TestWorkingAction(t *testing.T) {
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(actionStartMessage))
	expectedOutputEvent := `{"version":"v1","type":"action_event","body":{"meta":{"action_id":14},"status":"ok","error":"","output":{"greeting":"good day to you"}}}`
	dispatcher := &mockDispatcher{}

	// mock dispatcher to test dispatch works
	defaultActionDispatcher = dispatcher

	p := New()
	err := p.Run()
	if err != nil {
		t.Fatalf("Unable to run %s: %v", p.Name, err)
	}

	if dispatcher.result != expectedOutputEvent {
		t.Fatalf("Unexpected event output, got %s but expected %s", dispatcher.result, expectedOutputEvent)
	}
}

func TestActionWithInvalidMessageType(t *testing.T) {
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(invalidTypeActionStartMessage))

	p := New()
	err := p.Run()
	if err == nil {
		t.Fatal("Expected error running")
	}

	msg := "Unexpected message type: not_action_start"
	if err.Error() != msg {
		t.Fatalf("Expected '%s' but got %s", msg, err)
	}
}

func TestGenerateSampleActionStartMessage(t *testing.T) {
	action := &HelloAction{}

	sample := `{
   "version": "v1",
   "type": "action_start",
   "body": {
     "meta": null,
     "action": "hello_action",
     "connection": {
       "thing": ""
     },
     "dispatcher": {},
     "input": {
       "person": ""
     }
   }
 }`
	defaultActionDispatcher = &StdoutDispatcher{}
	p, err := GenerateSampleActionStart(action)

	if err != nil {
		t.Fatal(err)
	}

	if p != sample {
		t.Fatalf("Expected action start to be equal: %s, expected: %s", p, sample)
	}

}
