package pulse.consent

default allow = false

allow {
  some scope
  scope := input.route
  input.user.scopes[_] == scope
}
