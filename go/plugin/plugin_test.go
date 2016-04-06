package plugin

import "testing"

type HelloPlugin struct {
	Plugin
}

func (t HelloPlugin) Vendor() string {
	return "komandsoft"
}

type TriggerNoName struct {
	Trigger
}

func (t *TriggerNoName) Name() string {
	return ""
}

func (t *TriggerNoName) Description() string {
	return ""
}

func (t *TriggerNoName) RunTrigger() error {
	return nil
}

func New() *HelloPlugin {
	h := &HelloPlugin{}
	h.Init(Meta{
		Name:        "",
		Description: "",
		Vendor:      "",
		Version:     "",
	})
	h.AddTrigger(&HelloTrigger{})
	h.AddAction(&HelloAction{})
	return h
}

func TestEmptyTriggerNameReturnsError(t *testing.T) {
	h := &HelloPlugin{}

	h.Init(Meta{
		Name:        "Hello",
		Description: "",
		Vendor:      "",
		Version:     "",
	})

	err := h.AddTrigger(&TriggerNoName{})

	expected := `No Name() was found for the trigger.`
	if err == nil {
		t.Fatal("Expected an error")
	}
	if err.Error() != expected {
		t.Fatalf("Expected %s but got %s", expected, err)
	}
}
