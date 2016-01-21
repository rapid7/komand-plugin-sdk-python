package plugin

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/orcalabs/plugin-sdk/go/plugin/messages"

	"github.com/satori/go.uuid"
)

func DispatchTriggerEvent(url string, output interface{}) error {
	uid := uuid.NewV4().String()

	eventBytes, err := json.Marshal(output)

	if err != nil {
		return err
	}

	trigger := messages.TriggerEvent{Uid: uid, Output: eventBytes}

	jsonStr, err := MarshalMessage("trigger_event", &trigger)

	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonStr))
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}

	resp, err := client.Do(req)

	if err != nil {
		return fmt.Errorf("Unable to send event: %+v", err)
	}

	defer resp.Body.Close()

	// TODO: check for good response status
	log.Println("response Status:", resp.Status)
	log.Println("response Headers:", resp.Header)
	body, _ := ioutil.ReadAll(resp.Body)
	log.Println("response Body:", string(body))
	return nil
}
