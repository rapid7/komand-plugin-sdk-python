package plugin

import (
	"github.com/orcalabs/plugin-sdk/go/plugin/message"
)

// actionTask task runner
type actionTask struct {
	dispatcher Dispatcher
	message    *message.ActionStart
	action     Actionable
}

// Run will start the action
func (a *actionTask) Run() error {
	// unpack the action connection and input configurations
	if err := a.unpack(); err != nil {
		return err
	}

	// connect the connection
	if connectable, ok := a.action.(Connectable); ok {
		if err := connectable.Connection().Connect(); err != nil {
			return err
		}
	}

	// perform the action
	if err := a.action.Act(); err != nil {
		return a.fail(err.Error())
	}

	// default output is empty
	var output interface{} = struct{}{}

	// use the output of the action as the argument to 'done'
	if outputable, ok := a.action.(Outputable); ok {
		output = outputable.Output()
	}
	return a.success(output)
}

// Success will complete the action
func (a *actionTask) success(output Output) error {
	return a.emit("", output)
}

// fail will write the error message
func (a *actionTask) fail(err string) error {
	return a.emit(err, nil)
}

// emit emits a message to the dispatcher
func (a *actionTask) emit(err string, out Output) error {

	m := message.Message{
		Header: message.Header{
			Version: message.Version,
			Type:    "action_event",
		},
	}

	var e message.ActionResult
	if err != "" {
		e = message.ActionResult{
			ActionID: a.message.ActionID,
			Status:   "error",
			Error:    err,
		}

	} else {
		e = message.ActionResult{
			ActionID: a.message.ActionID,
			Status:   "ok",
			Output: message.OutputMessage{
				Contents: out,
			},
		}
	}

	m.Body.Contents = &e
	return a.dispatcher.Send(&m)
}

// unpack the ActionStart message into the task action
func (a *actionTask) unpack() error {

	msg := a.message

	if connectable, ok := a.action.(Connectable); ok {
		msg.Connection.Contents = connectable.Connection()
	}

	if inputable, ok := a.action.(Inputable); ok {
		msg.Input.Contents = inputable.Input()
	}

	// configure the dispatcher
	msg.Dispatcher.Contents = a.dispatcher

	return msg.Unpack()
}
