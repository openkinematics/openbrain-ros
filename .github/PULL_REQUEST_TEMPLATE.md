<!--
Thanks for sending a PR! Fill in the sections below — keep them short.
-->

## What

<!-- One paragraph: what does this PR change? -->

## Why

<!-- One paragraph: what problem does it solve / what does it enable? -->

## How tested

<!-- Bulleted list. Be specific about hardware vs sim vs CI-only. -->

- [ ] `make build` clean
- [ ] `make test` green
- [ ] `make lint` green
- [ ] Tested on hardware: <!-- robot + edge box, or "no" -->
- [ ] Tested in sim: <!-- yes / no -->

## Public-API impact

<!-- Does this touch openbrain_msgs/, the WebRTC streamer endpoints, the
     rosbridge surface area, or any service the dashboard calls? If yes,
     check the box and link the companion dashboard PR. -->

- [ ] Breaks the v1 contract documented in `docs/api.md`
- [ ] Companion PR in [openbrain-dashboard](https://github.com/openkinematics/openbrain-dashboard): #...

## Checklist

- [ ] Updated `CHANGELOG.md` (Unreleased section)
- [ ] Updated relevant package `README.md`
- [ ] DCO sign-off on every commit (`Signed-off-by:`)
