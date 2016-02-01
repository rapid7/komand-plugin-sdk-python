package message

import (
	"encoding/json"
	"testing"
)

var triggerStartMessage = `
{
  "version": "v1",
  "type": "trigger_start",
  "body": {
	 "trigger": "hello",
     "input": {},
	 "connection": {}
  }
}
`

func TestMessage(t *testing.T) {
	m := Message{}

	err := json.Unmarshal([]byte(triggerStartMessage), &m)
	if err != nil {
		t.Error("Error unmarshalling:", err)
	}

	if m.Version != "v1" {
		t.Error("Version is wrong, expected v1 but got", m.Version)
	}
	if m.Type != "trigger_start" {
		t.Error("Type is wrong, expected trigger_start but got", m.Type)
	}

}
