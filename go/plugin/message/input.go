package message

import "encoding/json"

// Input holds the input for the message
type Input struct {
	json.RawMessage `json:"input"`
	Contents        interface{}
}
