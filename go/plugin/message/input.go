package message

import "encoding/json"

// Input holds the input for the message
type Input struct {
	json.RawMessage
	Contents interface{}
}

func (i *Input) MarshalJSON() ([]byte, error) {
	if i.RawMessage == nil || len(i.RawMessage) == 0 {
		msg, err := json.Marshal(&i.Contents)
		if err != nil {
			return nil, err
		}
		i.RawMessage = msg
	}

	return i.RawMessage, nil
}
