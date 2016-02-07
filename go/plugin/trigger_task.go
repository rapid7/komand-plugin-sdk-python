package plugin

import (
	"errors"
	"fmt"
	"os"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
)

// triggerTask runs a trigger
type triggerTask struct {
	dispatcher Dispatcher
	message    *message.TriggerStart
	trigger    Triggerable
}

// Test the task
func (t *triggerTask) Test() error {

	// unpack the trigger connection and input configurations
	if err := t.unpack(); err != nil {
		return err
	}

	// connect the connection
	if connectable, ok := t.trigger.(Connectable); ok {
		if err := connectable.Connection().Connect(); err != nil {
			return fmt.Errorf("Connection test failed: %s", err)
		}
	}

	// if the trigger supports a test, run a test.
	if testable, ok := t.trigger.(Testable); ok {
		return testable.Test()
	}

	return nil
}

// Run the task
func (t *triggerTask) Run() error {

	// unpack the trigger connection and input configurations
	if err := t.unpack(); err != nil {
		return err
	}

	// connect the connection
	if connectable, ok := t.trigger.(Connectable); ok {
		if err := connectable.Connection().Connect(); err != nil {
			return err
		}
	}

	collector, err := newTriggerEventCollector(
		t.message.TriggerID,
		t.trigger,
		t.dispatcher,
	)

	if err != nil {
		return err
	}

	defer collector.stop()
	go collector.start()

	// finally start the trigger
	return t.trigger.RunTrigger()
}

// unpack unpacks the message into the trigger task object
func (t *triggerTask) unpack() error {

	if connectable, ok := t.trigger.(Connectable); ok {
		t.message.Connection.Contents = connectable.Connection()
	}

	if inputable, ok := t.trigger.(Inputable); ok {
		t.message.Input.Contents = inputable.Input()
	}

	t.message.Dispatcher.Contents = t.dispatcher

	return t.message.Unpack()
}

// triggerEventCollector will continuously collect events from the trigger queue
// and submit them to the dispatcher.
type triggerEventCollector struct {
	stopped    chan bool
	sender     queueable
	dispatcher Dispatcher
	triggerID  int

	errors chan error
}

func newTriggerEventCollector(triggerID int, trigger Triggerable, dispatcher Dispatcher) (*triggerEventCollector, error) {
	if queueable, ok := trigger.(queueable); ok {

		queueable.InitQueue()

		return &triggerEventCollector{
			triggerID:  triggerID,
			stopped:    make(chan bool, 1),
			sender:     queueable,
			dispatcher: dispatcher,
			errors:     make(chan error),
		}, nil
	}
	return nil, errors.New("Trigger does not implement Send() interface. Did you compose with plugin.Trigger?")
}

func (t *triggerEventCollector) start() {
	for {
		output := t.sender.Read()
		if output != nil {
			if err := t.send(output); err != nil {
				// TODO: remove this and figure out how to handle.
				fmt.Fprintf(os.Stderr, "Receieved error sending trigger message: %s", err)
				t.errors <- err
			}
		} else {
			break
		}
	}
	t.stopped <- true
}
func (t *triggerEventCollector) stop() {
	t.sender.Stop()
	<-t.stopped
}

// send will dispatch an output event
func (t *triggerEventCollector) send(event message.Output) error {

	m := message.Message{
		Header: message.Header{
			Version: message.Version,
			Type:    "trigger_event",
		},
	}

	e := message.TriggerEvent{
		TriggerID: t.triggerID,
		Output: message.OutputMessage{
			Contents: event,
		},
	}

	m.Body.Contents = &e
	return t.dispatcher.Send(&m)
}
