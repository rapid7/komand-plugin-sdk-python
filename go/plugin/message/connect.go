package message

import (
	"encoding/json"
	"fmt"
)

// Connectable must be implemented by Connections to work with a Plugin
type Connectable interface {
	Connect() error
}

// Connection is the default Connection Type
type Connection struct {
	json.RawMessage
	Contents interface{}
}

// Connect connects a Connection
func (c Connection) Connect() error {
	return fmt.Errorf("Failed to connect, Connect() not implemented.")
}
