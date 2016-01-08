package messages

import (
	"encoding/json"
	"testing"
)

func TestTriggerStartMessage(t *testing.T) {
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

	trigger := TriggerStart{}
	err = json.Unmarshal(m.Body, &trigger)
	if err != nil {
		t.Error("Error unmarshalling:", err)
	}

	if trigger.Trigger != "hello" {
		t.Error("trigger is wrong, expected hello but got", trigger)
	}
}
