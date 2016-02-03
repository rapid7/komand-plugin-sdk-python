package plugin

import (
	"strings"
	"testing"

	"github.com/orcalabs/plugin-sdk/go/plugin/parameter"
)

var actionStartMessage = `
{
  "version": "v1",
  "type": "action_start",
  "body": {
    "action_id": 14,
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
    "action_id": 14,
	  "action": "hello_action",
	  "connection": { "thing": "one"},
    "input": { "person": "Bob"}
  }
}
`

type HelloAction struct{}

func (a HelloAction) Act() error {
	return nil
}

func TestWorkingAction(t *testing.T) {
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(actionStartMessage))

	p := New()
	err := p.Run()
	if err != nil {
		t.Fatalf("Unable to run %s: %v", p.Name, err)
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
