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
	 "parameters": { "person": "Bob"},
	 "config": { "thing": "one"}
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
	 "parameters": { "person": "Bob"},
	 "config": { "thing": "one"}
  }
}
`

type HelloConfig struct {
	Thing string `json:"thing"`
}

type HelloParameters struct {
	Person string `json:"person"`
}

type HelloTrigger struct {
	Trigger
	config     HelloConfig
	parameters HelloParameters
}

func (ht *HelloTrigger) Name() string {
	return "hello"
}

func (ht *HelloTrigger) Parameters() interface{} {
	return &ht.parameters
}

func (ht *HelloTrigger) Config() interface{} {
	return &ht.config
}

func TestWorkingTrigger(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(triggerStartMessage))
	helloTrigger := &HelloTrigger{}
	helloTrigger.Init(helloTrigger)
	err := helloTrigger.ReadStart()

	if err != nil {
		t.Fatal("Unable to parse", err)
	}

	if helloTrigger.parameters.Person != "Bob" {
		t.Fatal("Expected Bob, got ", helloTrigger.parameters.Person)
	}

	if helloTrigger.config.Thing != "one" {
		t.Fatal("Expected one, got ", helloTrigger.config.Thing)
	}
}

func TestTriggerWithBadMsgType(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(badTriggerStartMessage))
	helloTrigger := &HelloTrigger{}
	helloTrigger.Init(helloTrigger)
	err := helloTrigger.ReadStart()
	if err == nil {
		t.Fatal("Expected error parsing")
	}

	msg := "Unexpected message type, wanted: trigger_start but got not_trigger_start"
	if err.Error() != msg {
		t.Fatal("Expected '%s' but got %s", msg, err)
	}

}
