package message

import (
	"encoding/json"
	"fmt"
)

// Header is appended to the top of every message
type Header struct {
	Version string          `json:"version"` // version of messages
	Type    string          `json:"type"`    // message type
	Meta    json.RawMessage `json:"meta"`    //meta information about the message
}

// Message contains general message information that other messages should embed
type Message struct {
	Header                 // Message header
	Body   json.RawMessage `json:"body"` // Message body
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

// UnmarshalBody unmarshalls a Body object
func (m *Message) UnmarshalBody(body interface{}) error {
	err := json.Unmarshal(m.Body, body)
	if err != nil {
		return fmt.Errorf("Unable to unmarshal Body: %+v", err)
	}
	return nil
}
