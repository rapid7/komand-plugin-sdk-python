package messages

import (
	"encoding/json"
	"fmt"
)

type Message struct {
	MessageEnvelope
	Body json.RawMessage `json:"body"` // body of data
}

// Validate the msg against the provided msgtype.
func (m *Message) Validate(msgtype string) error {
	if m.Version != Version {
		return fmt.Errorf("Unexpected version, wanted: %s but got %s", Version, m.Version)
	}
	if m.Type != msgtype {
		return fmt.Errorf("Unexpected message type, wanted: %s but got %s", msgtype, m.Type)
	}
	return nil
}

// UnmarshalBody unmarshals the message.Body into the `body` parameter
func (m *Message) UnmarshalBody(body interface{}) error {
	err := json.Unmarshal(m.Body, body)
	if err != nil {
		return fmt.Errorf("Unable to marshal Message.Body: %+v", err)
	}
	return nil
}
