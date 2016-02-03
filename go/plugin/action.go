package plugin

// Actionable must be implemented by Actions to work with Plugins
type Actionable interface {
	Act() error
}
