package message

import "encoding/json"

// Output holds the raw JSON for the Trigger or Action output
type Output struct {
	json.RawMessage
	Interface interface{} `json:"-"`
}
