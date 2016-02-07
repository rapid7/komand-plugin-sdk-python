package plugin

import "testing"

type HelloPlugin struct {
	Plugin
}

type TriggerNoName struct {
	Trigger
}

func (t *TriggerNoName) Name() string {
	return ""
}

func (t *TriggerNoName) RunTrigger() error {
	return nil
}

func New() *HelloPlugin {
	h := &HelloPlugin{}
	h.Init("Hello")
	h.AddTrigger(&HelloTrigger{})
	h.AddAction(&HelloAction{})
	return h
}

func TestEmptyTriggerNameReturnsError(t *testing.T) {
	h := &HelloPlugin{}
	h.Init("Hello")
	err := h.AddTrigger(&TriggerNoName{})

	expected := `No Name() was found for the trigger.`
	if err == nil {
		t.Fatal("Expected an error")
	}
	if err.Error() != expected {
		t.Fatalf("Expected %s but got %s", expected, err)
	}
}
