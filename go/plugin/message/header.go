package message

import "encoding/json"

// Meta defines meta-information about the Message
type Meta struct {
	json.RawMessage `json:"meta"`
	Contents        interface{}
}

// Header is appended to the top of every message
type Header struct {
	Version string `json:"version"` // version of messages
	Type    string `json:"type"`    // message type
	Meta    Meta   //meta information about the message
}
