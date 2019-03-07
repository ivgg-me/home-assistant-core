workflow "Python 3.7 - tox" {
  on = "push"
  resolves = ["Python 3.7 - tests"]
}

action "Python 3.7 - tests" {
  uses = "home-assistant/actions/py37-tox@master"
  args = "-e py37"
}

workflow "Python 3.6 - tox" {
  on = "push"
  resolves = ["Python 3.6 - tests"]
}

action "Python 3.6 - tests" {
  uses = "home-assistant/actions/py36-tox@master"
  args = "-e py36"
}

workflow "Python 3.5 - tox" {
  on = "push"
  resolves = ["Pyton 3.5 - typing"]
}

action "Python 3.5 - tests" {
  uses = "home-assistant/actions/py35-tox@master"
  args = "-e py35"
}

action "Python 3.5 - lints" {
  uses = "home-assistant/actions/py35-tox@master"
  needs = ["Python 3.5 - tests"]
  args = "-e lint"
}

action "Pyton 3.5 - typing" {
  uses = "home-assistant/actions/py35-tox@master"
  args = "-e typing"
  needs = ["Python 3.5 - lints"]
}
