package plugin

import (
	"encoding/json"
	"fmt"

	"github.com/orcalabs/plugin-sdk/go/messages"
)

type Trigger struct {
	DispatcherURL string
	Meta          messages.Meta

	config  interface{}
	params  interface{}
	trigger string
}

type TriggerVars interface {
	Config() interface{}
	Parameters() interface{}
	// Name of trigger
	Name() string
}

func (tp *Trigger) Init(vars TriggerVars) {
	tp.config = vars.Config()
	tp.params = vars.Parameters()
	tp.trigger = vars.Name()
}

func (tp *Trigger) Send(event interface{}) {
	DispatchTriggerEvent(tp.DispatcherURL, event, tp.Meta)
}

func (tp *Trigger) ReadStart() error {
	config := tp.config
	params := tp.params

	startMessage := &messages.TriggerStart{}
	msg, err := UnmarshalMessage("trigger_start", &startMessage)

	if err != nil {
		return err
	}

	tp.Meta = msg.Meta

	if startMessage.Trigger != tp.trigger {
		return fmt.Errorf("Expected trigger %s but got %s", tp.trigger, startMessage.Trigger)
	}

	err = json.Unmarshal(startMessage.Config, config)

	if err != nil {
		return fmt.Errorf("Unable to parse config %s", err)
	}

	err = json.Unmarshal(startMessage.Parameters, params)

	if err != nil {
		return fmt.Errorf("Unable to parse parameters %s", err)
	}
	return nil

}

func MarshalMessage(msgtype string, meta messages.Meta, body interface{}) ([]byte, error) {

	m := messages.Message{
		MessageEnvelope: messages.MessageEnvelope{
			Type:    msgtype,
			Version: messages.Version,
		},

		Meta: meta,
	}

	bodyBytes, err := json.Marshal(body)

	if err != nil {
		return nil, err
	}

	m.Body = bodyBytes

	return json.Marshal(&m)
}

func UnmarshalMessage(msgtype string, body interface{}) (*messages.Message, error) {
	m := messages.Message{}

	if err := Unmarshal(&m); err != nil {
		return nil, err
	}

	if err := m.Validate(msgtype); err != nil {
		return nil, err
	}

	if err := m.UnmarshalBody(body); err != nil {
		return nil, fmt.Errorf("Unable to marshal Message.Body: %+v", err)
	}

	return &m, nil
}
