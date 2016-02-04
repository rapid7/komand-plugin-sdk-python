package connect

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

func (c *Connection) MarshalJSON() ([]byte, error) {
	if c.RawMessage == nil || len(c.RawMessage) == 0 {
		msg, err := json.Marshal(&c.Contents)
		if err != nil {
			return nil, err
		}
		c.RawMessage = msg
	}

	return c.RawMessage, nil
}
