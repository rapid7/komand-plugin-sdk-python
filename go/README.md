# Orca Plugin SDK
To create the skeleton for a new plugin, run the code generator.
To make a plugin compatible with the system implement the methods defined in the interfaces of Pluginable: `Connect() and Test()`
```go

// Connector is an interface that a type must satisfy if it wants to create a connection within a Plugin
type Connector interface {
	Connect() error
}

// Tester is an interface that a type must satisfy if it wants to be testable within a Plugin
type Tester interface {
	Test() error
}

// Pluginable is an interface that all plugins should implemented
type Pluginable interface {
	Connector
	Tester
}
```
