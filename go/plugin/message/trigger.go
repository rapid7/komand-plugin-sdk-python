package message

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/orcalabs/plugin-sdk/go/plugin/connect"
	"github.com/orcalabs/plugin-sdk/go/plugin/parameter"
)

// TriggerStart is the format of the message that starts a Trigger
type TriggerStart struct {
	TriggerID     int                `json:"trigger_id"`     // TriggerId that identifies the trigger in the system
	Connection    connect.Connection `json:"connection"`     // Connection is the global connection for the plugin
	DispatcherURL string             `json:"dispatcher_url"` // Dispatcher URL is the url for the channel
	Trigger       string             `json:"trigger"`        // Trigger is the name of the trigger
	Input         Input              // Input are the parameters passed to trigger start
}

// Read reads the start message for the Plugin
func (m *TriggerStart) Read() error {
	if err := parameter.Unmarshal(&m); err != nil {
		return err
	}

	err := json.Unmarshal(m.Connection.RawMessage, m.Connection.Contents)
	if err != nil {
		return fmt.Errorf("Unable to parse connection %s", err)
	}

	err = json.Unmarshal(m.Input.RawMessage, m.Input.Contents)
	if err != nil {
		return fmt.Errorf("Unable to parse input %s", err)
	}

	return nil
}

// TriggerEvent is the format of the event message that a Trigger emits
// TODO: make this match the models
type TriggerEvent struct {
	TriggerID int `json:"trigger_id"`
	Output    Output
}

// Dispatch dispatches a trigger event
func (e *TriggerEvent) Dispatch(url string) error {
	jsonStr, err := json.Marshal(&e)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonStr))
	if err != nil {
		log.Fatal("Could not create POST request:", err)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	defer resp.Body.Close()
	if err != nil {
		return fmt.Errorf("Unable to send event: %+v", err)
	}

	// TODO: check for good response status
	log.Println("response Status:", resp.Status)
	log.Println("response Headers:", resp.Header)
	body, _ := ioutil.ReadAll(resp.Body)
	log.Println("response Body:", string(body))
	return nil
}
