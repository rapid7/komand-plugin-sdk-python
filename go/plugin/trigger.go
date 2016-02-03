package plugin

import (
	"errors"

	"github.com/orcalabs/plugin-sdk/go/plugin/message"
)

// Triggerable is the interface for a Trigger within a Plugin
type Triggerable interface {
	Trigger() error
}

// Trigger defines a struct that can be embedded within any implemented Trigger
type Trigger struct {
	ID            int
	Name          string
	DispatcherURL string
	Input         *message.Input
}

// Trigger triggers the trigger
func (t Trigger) Trigger() error {
	return errors.New("Failed to trigger, Trigger() not implemented.")
}

// Send will dispatch a trigger event
func (t *Trigger) Send(d message.Dispatchable) error {
	return d.Dispatch(t.DispatcherURL)
}
