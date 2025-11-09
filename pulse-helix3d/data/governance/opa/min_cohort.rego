package pulse.min_cohort

default allow = false

allow {
  input.route == "dashboard.analytics"
  input.user.tier != "core"
}

allow {
  input.route != "dashboard.analytics"
}
