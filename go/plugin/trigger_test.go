package plugin

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
	"github.com/orcalabs/plugin-sdk/go/plugin/parameter"
)

var triggerTestStartMessage = `
{
  "version": "v1",
  "type": "trigger_start",
  "meta": {
	  "channel": "xyz-abc-123"
  },
  "body": {
	  "dispatcher": { "url": "http://localhost:8000/blah" },
	  "trigger": "testable_trigger",
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
	  "dispatcher": { "url": "http://localhost:8000/blah" },
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
	  "dispatcher": { "url": "http://localhost:8000/blah" },
	  "trigger": "hello_trigger",
	  "input": { "person": "Bob"},
	  "connection": { "thing": "one"}
  }
}
`

type HelloTrigger struct {
	Trigger
	connection HelloConnection
	input      HelloInput

	testRan bool
}

func (t *HelloTrigger) Name() string {
	return "hello_trigger"
}

type HelloOutput struct {
	Goodbye string
}

func (t *HelloTrigger) RunTrigger() error {
	return t.Send(&HelloOutput{Goodbye: "bob"})
}

// Connection() implements the Connectable interface
func (t *HelloTrigger) Connection() Connection {
	return &t.connection
}

// Input() will implemnent the Inputable interface
func (t *HelloTrigger) Input() Input {
	return &t.input
}

type HelloConnection struct {
	Thing     string `json:"thing"`
	connected bool
}

type HelloInput struct {
	Person string `json:"person"`
}

func (c *HelloInput) Validate() []error {
	return nil
}

func (c *HelloConnection) Validate() []error {
	// It would actually connect
	return nil
}

// Connect will implement the connection interface
func (c *HelloConnection) Connect() error {
	c.connected = true
	// It would actually connect
	return nil
}

type mockDispatcher struct {
	URL    string `json:"url"`
	result string
}

func (m *mockDispatcher) Send(msg *message.Message) error {
	result, err := json.Marshal(msg)
	if err == nil {
		m.result = string(result)
	}
	return err
}

func TestWorkingTrigger(t *testing.T) {

	trigger := &HelloTrigger{}

	expectedOutputEvent := `{"version":"v1","type":"trigger_event","body":{"trigger_id":0,"output":{"Goodbye":"bob"}}}`
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(triggerStartMessage))

	dispatcher := &mockDispatcher{}

	// mock dispatcher to test dispatch works
	defaultTriggerDispatcher = dispatcher

	p := &HelloPlugin{}
	p.Plugin.Init("hello")
	p.AddTrigger(trigger)

	err := p.Run()

	if err != nil {
		t.Fatalf("Unable to run %s: %v", p.Name, err)
	}

	if trigger.input.Person != "Bob" {
		t.Fatal("Expected Bob, got ", trigger.input.Person)
	}

	if trigger.connection.Thing != "one" {
		t.Fatal("Expected one, got ", trigger.connection.Thing)
	}

	if !trigger.connection.connected {
		t.Fatal("Expected trigger connection to connect")
	}

	if dispatcher.URL != "http://localhost:8000/blah" {
		t.Fatal("Expected dispatcher url to be http://localhost:8000/blah, got ", dispatcher.URL)
	}

	if dispatcher.result != expectedOutputEvent {
		t.Fatalf("Unexpected event output, got %s but expected %s", dispatcher.result, expectedOutputEvent)
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

type TestableTrigger struct {
	Trigger
	testRan bool
}

func (t *TestableTrigger) Name() string {
	return "testable_trigger"
}

func (t *TestableTrigger) RunTrigger() error {
	t.testRan = false
	return nil
}

func (t *TestableTrigger) Test() error {
	t.testRan = true
	return nil
}

func TestRunPluginTriggerWithTestRunsTest(t *testing.T) {

	trigger := &TestableTrigger{}
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(triggerTestStartMessage))

	dispatcher := &mockDispatcher{}
	// mock dispatcher to test dispatch works
	defaultTriggerDispatcher = dispatcher

	p := &HelloPlugin{}
	p.Init("hello")
	p.AddTrigger(trigger)

	err := p.Test()

	if err != nil {
		t.Fatalf("Unable to test %s: %v", p.Name, err)
	}

	if trigger.testRan != true {
		t.Fatal("The testable trigger test did not run")
	}

}

func TestRunPluginTriggerWithoutTestDoesNothing(t *testing.T) {

	trigger := &HelloTrigger{}
	parameter.Stdin = parameter.NewParamSet(strings.NewReader(triggerStartMessage))

	dispatcher := &mockDispatcher{}
	// mock dispatcher to test dispatch works
	defaultTriggerDispatcher = dispatcher

	p := &HelloPlugin{}
	p.Init("hello")
	p.AddTrigger(trigger)

	err := p.Test()

	if err != nil {
		t.Fatalf("Unable to test %s: %v", p.Name, err)
	}

	if trigger.testRan != false {
		t.Fatal("Expected testRan to be false because this trigger has no test")
	}
}
