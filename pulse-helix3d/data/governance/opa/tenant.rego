package pulse.tenant

default allow = false

allow {
  input.tenant == data.tenants[_]
}
