package plugin

import (
	"strings"
	"testing"
)

var badActionStartMessage = `
{
  "version": "v1",
  "type": "not_action_start",
  "meta": {
	"channel": "xyz-abc-123"
  },
  "body": {
	 "action": "goodbye",
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
     "action_id": 1,
	 "action": "goodbye",
	 "connection": { "thing": "one"},
	 "input": { "person": "Bob"}
  }
}
`

type Goodbyeconnection struct {
	Thing string `json:"thing"`
}

type GoodbyeInput struct {
	Person string `json:"person"`
}

type GoodbyeAction struct {
	Action
	connection Goodbyeconnection
	input      GoodbyeInput
}

func (ht *GoodbyeAction) Name() string {
	return "goodbye"
}

func (ht *GoodbyeAction) Input() interface{} {
	return &ht.input
}

func (ht *GoodbyeAction) Connection() interface{} {
	return &ht.connection
}

func TestWorkingAction(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(actionStartMessage))
	goodbyeAction := &GoodbyeAction{}
	goodbyeAction.Init(goodbyeAction)
	err := goodbyeAction.Run()

	if err != nil {
		t.Fatal("Unable to parse", err)
	}

	if goodbyeAction.input.Person != "Bob" {
		t.Fatal("Expected Bob, got ", goodbyeAction.input.Person)
	}

	if goodbyeAction.connection.Thing != "one" {
		t.Fatal("Expected one, got ", goodbyeAction.connection.Thing)
	}
}

func TestActionWithBadMsgType(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(badActionStartMessage))
	goodbyeAction := &GoodbyeAction{}
	goodbyeAction.Init(goodbyeAction)
	err := goodbyeAction.Run()
	if err == nil {
		t.Fatal("Expected error parsing")
	}

	msg := "Unexpected message type, wanted: action_start but got not_action_start"
	if err.Error() != msg {
		t.Fatalf("Expected '%s' but got %s", msg, err)
	}

}
