package message

import "encoding/json"

// Body holds the message body
type Body struct {
	json.RawMessage `json:"body"`
	Contents        interface{}
}

// MarshalJSON marshals a Body object
func (b *Body) MarshalJSON() ([]byte, error) {
	bodyBytes, err := json.Marshal(b.Contents)
	if err != nil {
		return nil, err
	}
	return bodyBytes, nil
}
