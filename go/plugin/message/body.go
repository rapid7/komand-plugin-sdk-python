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

// UnmarshalJSON unmarshalls a Body object
// func (b *Body) UnmarshalJSON(data []byte) error {
// 	fmt.Println(string(data))
// 	err := json.Unmarshal(b.RawMessage, b.Contents)
// 	if err != nil {
// 		return fmt.Errorf("Unable to unmarshal Body: %+v", err)
// 	}
// 	return nil
// }
