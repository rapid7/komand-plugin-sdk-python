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

	t.dispatcher = &StdoutDispatcher{}

	// connect the connection
	if connectable, ok := t.trigger.(Connectable); ok {
		if err := connectable.Connection().Connect(); err != nil {
			return fmt.Errorf("Connection test failed: %s", err)
		}
	}

	// if the trigger supports a test, run a test.
	if testable, ok := t.trigger.(Testable); ok {
		output, err := testable.Test()
		if err != nil {
			return err
		}

		if output != nil {
			m := makeTriggerEvent(t.message.TriggerID, output)
			err := t.dispatcher.Send(m)
			if err != nil {
				return err
			}
		}
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

	// start event collection
	collector, err := makeTriggerEventCollector(
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

	connectable, _ := t.trigger.(Connectable)
	inputable, _ := t.trigger.(Inputable)

	if connectable != nil {
		t.message.Connection.Contents = connectable.Connection()
	}

	if inputable != nil {
		t.message.Input.Contents = inputable.Input()
	}

	t.message.Dispatcher.Contents = t.dispatcher

	if err := t.message.Unpack(); err != nil {
		return err
	}

	if connectable != nil {
		if err := clean(connectable.Connection().Validate()); err != nil {
			return fmt.Errorf("Connection validation failed: %s", joinErrors(err))

		}
	}

	if inputable != nil {
		if err := clean(inputable.Input().Validate()); err != nil {
			return fmt.Errorf("Input validation failed: %s", joinErrors(err))

		}
	}
	return nil
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

func makeTriggerEventCollector(triggerID int, trigger Triggerable, dispatcher Dispatcher) (*triggerEventCollector, error) {
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
	m := makeTriggerEvent(t.triggerID, event)
	return t.dispatcher.Send(m)
}

func makeTriggerEvent(id int, output message.Output) *message.Message {
	m := message.Message{
		Header: message.Header{
			Version: message.Version,
			Type:    "trigger_event",
		},
	}

	e := message.TriggerEvent{
		TriggerID: id,
		Output: message.OutputMessage{
			Contents: output,
		},
	}

	m.Body.Contents = &e
	return &m
}
