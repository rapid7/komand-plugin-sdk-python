package plugin

// Triggerable must be implemented by a plugin trigger.
type Triggerable interface {
	RunTrigger() error // RunTrigger will run the trigger.
	Name() string      // Name is the trigger name
}

// Trigger defines a struct that should be embedded within any
// implemented Trigger.
type Trigger struct {
	name string
	sendQueue
}

// Init initializes the trigger with the trigger name.
func (t *Trigger) Init(name string) {
	t.name = name
	t.sendQueue.InitQueue()
}

// Name of the trigger
func (t *Trigger) Name() string {
	return t.name
}

// Send emits an event
func (t *Trigger) Send(event Output) error {
	return t.sendQueue.Send(event)
}
