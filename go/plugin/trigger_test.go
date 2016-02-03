package plugin

import (
	"strings"
	"testing"

	"github.com/orcalabs/plugin-sdk/go/plugin/parameter"
)

var triggerStartMessage = `
{
  "version": "v1",
  "type": "trigger_start",
  "meta": {
	  "channel": "xyz-abc-123"
  },
  "body": {
    "dispatcher_url": "http://localhost:8000/blah",
	  "trigger": "hello_trigger",
	  "input": { "person": "Bob"},
	  "connection": { "thing": "one"}
  }
}
`

var invalidTypeTriggerStartMessage = `
{
  "version": "v1",
  "type": "not_trigger_start",
  "meta": {
	  "channel": "xyz-abc-123"
  },
  "body": {
    "dispatcher_url": "http://localhost:8000/blah",
	  "trigger": "hello_trigger",
	  "input": { "person": "Bob"},
	  "connection": { "thing": "one"}
  }
}
`

type HelloTrigger struct{}

func (t HelloTrigger) Trigger() error {
	return nil
}

func TestWorkingTrigger(t *testing.T) {
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(triggerStartMessage))

	p := New()
	err := p.Run()
	if err != nil {
		t.Fatalf("Unable to run %s: %v", p.Name, err)
	}
}

func TestInvalidTriggerStartMessageType(t *testing.T) {
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(invalidTypeTriggerStartMessage))

	p := New()
	err := p.Run()

	msg := "Unexpected message type: not_trigger_start"
	if err.Error() != msg {
		t.Fatalf("Expected '%s' but got %s", msg, err)
	}
}
