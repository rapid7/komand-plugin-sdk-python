package plugin

type HelloPlugin struct {
	Plugin
}

func New() *HelloPlugin {
	h := &HelloPlugin{}
	h.Init("Hello")
	h.AddTrigger(&HelloTrigger{})
	h.AddAction(&HelloAction{})
	return h
}
