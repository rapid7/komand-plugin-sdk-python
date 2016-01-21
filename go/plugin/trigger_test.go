package plugin

import (
	"strings"
	"testing"
)

var badTriggerStartMessage = `
{
  "version": "v1",
  "type": "not_trigger_start",
  "meta": {
	"channel": "xyz-abc-123"
  },
  "body": {
	 "trigger": "hello",
	 "input": { "person": "Bob"},
	 "connection": { "thing": "one"}
  }
}
`

var triggerStartMessage = `
{
  "version": "v1",
  "type": "trigger_start",
  "meta": {
	"channel": "xyz-abc-123"
  },
  "body": {
     "dispatcher_url": "http://localhost:8000/blah",
	 "trigger": "hello",
	 "input": { "person": "Bob"},
	 "connection": { "thing": "one"}
  }
}
`

type HelloConnection struct {
	Thing string `json:"thing"`
}

type HelloInput struct {
	Person string `json:"person"`
}

type HelloTrigger struct {
	Trigger
	connection HelloConnection
	input      HelloInput
}

func (ht *HelloTrigger) Name() string {
	return "hello"
}

func (ht *HelloTrigger) Input() interface{} {
	return &ht.input
}

func (ht *HelloTrigger) Connection() interface{} {
	return &ht.connection
}

func TestWorkingTrigger(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(triggerStartMessage))
	vars := &TriggerVars{}
	helloTrigger := &HelloTrigger{}
	helloTrigger.Init(vars)
	err := helloTrigger.ReadStart()

	if err != nil {
		t.Fatal("Unable to parse", err)
	}

	if helloTrigger.input.Person != "Bob" {
		t.Fatal("Expected Bob, got ", helloTrigger.input.Person)
	}

	if helloTrigger.connection.Thing != "one" {
		t.Fatal("Expected one, got ", helloTrigger.connection.Thing)
	}
}

func TestTriggerWithBadMsgType(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(badTriggerStartMessage))
	vars := &TriggerVars{}
	helloTrigger := &HelloTrigger{}
	helloTrigger.Init(vars)
	err := helloTrigger.ReadStart()
	if err == nil {
		t.Fatal("Expected error parsing")
	}

	msg := "Unexpected message type, wanted: trigger_start but got not_trigger_start"
	if err.Error() != msg {
		t.Fatal("Expected '%s' but got %s", msg, err)
	}

}
