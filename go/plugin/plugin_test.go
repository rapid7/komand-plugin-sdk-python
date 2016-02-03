package plugin

import (
	"strings"
	"testing"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
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

var actionStartMessage = `
{
  "version": "v1",
  "type": "action_start",
  "meta": {
	  "channel": "xyz-abc-123"
  },
  "body": {
    "action_id": 14,
	  "action": "hello_action",
	  "connection": { "thing": "one"},
    "input": { "person": "Bob"},
  }
}
`

type HelloTrigger struct{}

func (t HelloTrigger) Trigger() error {
	return nil
}

type HelloAction struct{}

func (a HelloAction) Act() error {
	return nil
}

type HelloPlugin struct {
	Plugin
}

func New() *HelloPlugin {
	h := &HelloPlugin{}
	h.Plugin.Init()

	h.Name = "hello"
	h.AddTrigger("hello_trigger", &HelloTrigger{})
	h.AddAction("hello_action", &HelloAction{})
	return h
}

func (p HelloPlugin) Run() error {
	err := p.Plugin.Run()
	if err != nil {
		return err
	}
	return nil
}

func (p HelloPlugin) Connect(c message.Connectable) error {
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

func TestWorkingAction(t *testing.T) {
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(actionStartMessage))

	p := New()
	err := p.Run()
	if err != nil {
		t.Fatalf("Unable to run %s: %v", p.Name, err)
	}
}
