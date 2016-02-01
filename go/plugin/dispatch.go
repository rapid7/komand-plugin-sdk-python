package plugin

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
)

// DispatchTriggerEvent dispatches a trigger event
func DispatchTriggerEvent(url string, output interface{}) error {
	eventBytes, err := json.Marshal(output)
	if err != nil {
		return err
	}

	e := message.TriggerEvent{}
	err = e.Init()
	if err != nil {
		log.Fatal("Could not initialize Trigger Event")
	}
	e.Output.RawMessage = eventBytes

	jsonStr, err := e.MarshalJSON()
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
