package plugin

import (
	"encoding/json"
	"fmt"

	"github.com/orcalabs/plugin-sdk/go/messages"
)

func MarshalMessage(msgtype string, meta messages.Meta, body interface{}) ([]byte, error) {

	m := messages.Message{
		MessageEnvelope: messages.MessageEnvelope{
			Type:    msgtype,
			Version: messages.Version,
		},

		Meta: meta,
	}

	bodyBytes, err := json.Marshal(body)

	if err != nil {
		return nil, err
	}

	m.Body = bodyBytes

	return json.Marshal(&m)
}

func UnmarshalMessage(msgtype string, body interface{}) (*messages.Message, error) {
	m := messages.Message{}

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
