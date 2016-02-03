package plugin

import "github.com/orcalabs/plugin-sdk/go/plugin/connect"

type HelloPlugin struct {
	Plugin
}

func New() *HelloPlugin {
	h := &HelloPlugin{}
	h.Plugin.Init()
	h.Name = "hello"
	h.AddTrigger("hello_trigger", &HelloTrigger{})
	h.AddAction("hello_action", &HelloAction{})

	return h
}

func (p HelloPlugin) Run() error {
	err := p.Plugin.Run()
	if err != nil {
		return err
	}
	return nil
}

func (p HelloPlugin) Connect(c connect.Connectable) error {
	return nil
}
