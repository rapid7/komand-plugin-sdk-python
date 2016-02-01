package message

import (
	"encoding/json"
	"fmt"
)

// Header is appended to the top of every message
type Header struct {
	UID     string `json:"uid"`     // UID contains a unique identifier for the Message
	Version string `json:"version"` // version of messages
	Type    string `json:"type"`    // message type
}

// Body contains the specific type of message
type Body struct {
	json.RawMessage
	Contents interface{} `json:"-"`
}

// Unmarshal unmarshalls a Body object
func (b *Body) Unmarshal() (*Body, error) {
	err := json.Unmarshal(b.RawMessage, b.Contents)
	if err != nil {
		return nil, fmt.Errorf("Unable to unmarshal Body: %+v", err)
	}
	return b, nil
}

// Message contains general message information that other messages should embed
type Message struct {
	Header // Message header
	Body   // Message body
}

// Validate the msg against the provided msgtype.
func (m *Message) Validate() error {
	if m.Version != Version {
		return fmt.Errorf("Unexpected version, wanted: %s but got %s", Version, m.Version)
	}
	return nil
}

// Marshal marshals a Message object
func (m *Message) Marshal(msgType string, body interface{}) ([]byte, error) {
	m.Type = msgType
	m.Version = Version

	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}

	m.Body.RawMessage = bodyBytes

	return json.Marshal(&m)
}

// Unmarshal unmarshals a Message object
func (m *Message) Unmarshal() (*Message, error) {

	if err := Unmarshal(&m); err != nil {
		return nil, err
	}

	if err := m.Validate(); err != nil {
		return nil, err
	}

	if _, err := m.Body.Unmarshal(); err != nil {
		return nil, fmt.Errorf("Unable to unmarshal Message.Body: %+v", err)
	}

	return m, nil
}
