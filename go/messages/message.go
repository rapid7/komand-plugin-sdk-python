break
package messages

import (
	"encoding/json"
	"fmt"
)

type Message struct {
	MessageEnvelope
	Meta Meta            `json:"meta"` // meta data about channel
	Body json.RawMessage `json:"body"` // body of data
}

// Meta provides metadata about the channel, included with each message
type Meta struct {
	// Channel is the unique string id for the channel
	Channel string `json:"channel"`
}

func (m *Message) Validate(msgtype string) error {
	if m.Version != Version {
		return fmt.Errorf("Unexpected version, wanted: %s but got %s", Version, m.Version)
	}
	if m.Type != msgtype {
		return fmt.Errorf("Unexpected message type, wanted: %s but got %s", msgtype, m.Type)
	}
	return nil
}

func (m *Message) UnmarshalBody(body interface{}) error {
	err := json.Unmarshal(m.Body, body)
	if err != nil {
		return fmt.Errorf("Unable to marshal Message.Body: %+v", err)
	}
	return nil
}
