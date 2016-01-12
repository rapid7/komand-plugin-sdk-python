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
	 "parameters": { "person": "Bob"},
	 "config": { "thing": "one"}
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
	 "config": { "thing": "one"},
	 "parameters": { "person": "Bob"}
  }
}
`

type GoodbyeConfig struct {
	Thing string `json:"thing"`
}

type GoodbyeParameters struct {
	Person string `json:"person"`
}

type GoodbyeAction struct {
	Action
	config     GoodbyeConfig
	parameters GoodbyeParameters
}

func (ht *GoodbyeAction) Name() string {
	return "goodbye"
}

func (ht *GoodbyeAction) Parameters() interface{} {
	return &ht.parameters
}

func (ht *GoodbyeAction) Config() interface{} {
	return &ht.config
}

func TestWorkingAction(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(actionStartMessage))
	goodbyeAction := &GoodbyeAction{}
	goodbyeAction.Init(goodbyeAction)
	err := goodbyeAction.ReadStart()

	if err != nil {
		t.Fatal("Unable to parse", err)
	}

	if goodbyeAction.parameters.Person != "Bob" {
		t.Fatal("Expected Bob, got ", goodbyeAction.parameters.Person)
	}

	if goodbyeAction.config.Thing != "one" {
		t.Fatal("Expected one, got ", goodbyeAction.config.Thing)
	}
}

func TestActionWithBadMsgType(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(badActionStartMessage))
	goodbyeAction := &GoodbyeAction{}
	goodbyeAction.Init(goodbyeAction)
	err := goodbyeAction.ReadStart()
	if err == nil {
		t.Fatal("Expected error parsing")
	}

	msg := "Unexpected message type, wanted: action_start but got not_action_start"
	if err.Error() != msg {
		t.Fatal("Expected '%s' but got %s", msg, err)
	}

}
