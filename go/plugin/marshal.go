package plugin

import (
	"encoding/json"
	"fmt"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
)

// MarshalMessage marshals a message of type msgtype out of the body interface
func MarshalMessage(msgtype string, body interface{}) ([]byte, error) {

	m := message.Message{
		Header: message.Header{
			Type:    msgtype,
			Version: message.Version,
		},
	}

	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}

	m.Body = bodyBytes

	return json.Marshal(&m)
}

// UnmarshalMessage unmarshals a message of type msgtype into the body interface
func UnmarshalMessage(msgtype string, body interface{}) (*message.Message, error) {
	m := message.Message{}

	if err := Unmarshal(&m); err != nil {
		return nil, err
	}

	if err := m.Validate(msgtype); err != nil {
		return nil, err
	}

	if err := m.UnmarshalBody(body); err != nil {
		return nil, fmt.Errorf("Unable to marshal Message.Body: %+v", err)
	}

	return &m, nil
}
