package message

import (
	"encoding/json"
	"testing"
)

func TestMarshalTriggerStartWithMessageEnvelope(t *testing.T) {

	expected := `{"version":"v1","type":"trigger_start","body":{"trigger_id":1,"trigger":"hello","connection":{"username":"hello","password":"blah"},"dispatcher":{"url":"http://abc123"},"input":{"param":"ok","param2":"blah"}}}`

	connJSON := `
	{
		"username": "hello",
		"password": "blah"
	}
	`
	msg := json.RawMessage([]byte(connJSON))
	conn := ConnectionConfig{
		RawMessage: msg,
		Contents:   nil,
	}

	inputJSON := `
	{
		"param": "ok",
		"param2": "blah"
	}
	`
	msg = json.RawMessage([]byte(inputJSON))
	input := InputConfig{
		msg,
		nil,
	}

	dispatcherJSON := `
	{
		"url": "http://abc123"
	}
	`

	msg = json.RawMessage([]byte(dispatcherJSON))
	dispatcher := DispatcherConfig{
		msg,
		nil,
	}

	trig := &TriggerStart{
		TriggerID: 1,
		Trigger:   "hello",
		startMessage: startMessage{
			Connection: conn,
			Dispatcher: dispatcher,
			Input:      input,
		},
	}

	m := Message{
		Header: Header{
			Version: "v1",
			Type:    "trigger_start",
		},
	}

	str, err := m.MarshalBody(trig)

	if err != nil {
		t.Fatal("Unable to marshal: ", err)
	}

	if string(str) != expected {
		t.Fatalf("Got %s but expected %s", str, expected)
	}

}

func TestMarshalTriggerStart(t *testing.T) {
	expected := `{"trigger_id":1,"trigger":"hello","connection":{"username":"hello","password":"blah"},"dispatcher":{"url":"http://abc123"},"input":{"param":"ok","param2":"blah"}}`

	connJSON := `
	{
		"username": "hello",
		"password": "blah"
	}
	`
	msg := json.RawMessage([]byte(connJSON))
	conn := ConnectionConfig{
		RawMessage: msg,
		Contents:   nil,
	}

	inputJSON := `
	{
		"param": "ok",
		"param2": "blah"
	}
	`
	msg = json.RawMessage([]byte(inputJSON))
	input := InputConfig{
		msg,
		nil,
	}

	dispatcherJSON := `
	{
		"url": "http://abc123"
	}
	`

	msg = json.RawMessage([]byte(dispatcherJSON))
	dispatcher := DispatcherConfig{
		msg,
		nil,
	}

	trig := &TriggerStart{
		TriggerID: 1,
		Trigger:   "hello",
		startMessage: startMessage{
			Connection: conn,
			Dispatcher: dispatcher,
			Input:      input,
		},
		// Dispatcher: dispatcher,
		// Input:      input,
	}
	str, err := json.Marshal(trig)

	if err != nil {
		t.Fatal("Unable to marshal: ", err)
	}

	if string(str) != expected {
		t.Fatalf("Got %s but expected %s", str, expected)
	}
}
