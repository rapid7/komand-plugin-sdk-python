package plugin

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/orcalabs/plugin-sdk/go/messages"
)

type TestEvent struct {
	OogaBooga string
}

func TestTriggerFormatting(t *testing.T) {
	Stdin = NewParamSet(strings.NewReader(triggerStartMessage))
	helloTrigger := &HelloTrigger{}
	helloTrigger.Init(helloTrigger)
	err := helloTrigger.ReadStart()

	if err != nil {
		t.Fatal("Unable to parse", err)
	}

	testEvent := TestEvent{OogaBooga: "12345"}

	eventBytes, err := json.Marshal(&testEvent)

	if err != nil {
		t.Fatal(err)
	}

	ev := &messages.TriggerEvent{TriggerID: 100, Uid: "my-uid", Event: eventBytes}

	jsonStr, err := MarshalMessage("trigger_event", ev)

	if err != nil {
		t.Fatal(err)
	}

	str := string(jsonStr)

	expected := `{"version":"v1","type":"trigger_event","body":{"trigger_id":100,"uid":"my-uid","event":{"OogaBooga":"12345"}}}`

	if str != expected {
		t.Fatal("unexpected string", str, "wanted:", expected)
	}

}
