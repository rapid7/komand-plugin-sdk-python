package message

import "encoding/json"

// Input holds the raw JSON for the Trigger or Action input
type Input struct {
	json.RawMessage
	Contents interface{} `json:"-"`
}

// UnmarshalJSON unmarhsals the json.RawMessage into the Inputs Contents
func (i *Input) UnmarshalJSON(b []byte) error {
	return nil
}
