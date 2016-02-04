package message

import (
	"encoding/json"
	"testing"
)

import "github.com/orcalabs/plugin-sdk/go/plugin/connect"

func TestMarshalTriggerStart(t *testing.T) {
	expected := `{"trigger_id":1,"connection":{"username":"hello","password":"blah"},"dispatcher_url":"http://abc123","trigger":"hello","input":{"param":"ok","param2":"blah"}}`

	connJson := `
	{
		"username": "hello",
		"password": "blah"
	}	
	`
	msg := json.RawMessage([]byte(connJson))
	conn := connect.Connection{
		msg,
		nil,
	}

	inputJson := `
	{
		"param": "ok",
		"param2": "blah"
	}	
	`
	msg = json.RawMessage([]byte(inputJson))
	input := Input{
		msg,
		nil,
	}

	trig := &TriggerStart{
		Connection:    conn,
		TriggerID:     1,
		DispatcherURL: "http://abc123",
		Trigger:       "hello",
		Input:         input,
	}
	str, err := json.Marshal(trig)

	if err != nil {
		t.Fatal("Unable to marshal: ", err)
	}

	if str != expected {
		t.Fatalf("Got %s but expected %s", str, expected)
	}
}
