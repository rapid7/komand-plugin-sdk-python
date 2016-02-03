package message

import "encoding/json"

// Output holds the input for the message
type Output struct {
	json.RawMessage `json:"input"`
	Contents        interface{}
}
