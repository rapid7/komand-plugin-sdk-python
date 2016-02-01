package plugin

import "encoding/json"

// Connection defines a Plugin connection
type Connection struct {
	json.RawMessage
	Contents interface{}
}
