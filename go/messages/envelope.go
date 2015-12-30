package messages

// MessageEnvelope surrounds every message that comes in
type MessageEnvelope struct {
	Version string `json:"version"` // version of messages
	Type    string `json:"type"`    // message type
}
