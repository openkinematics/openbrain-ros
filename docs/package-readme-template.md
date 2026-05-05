# Package README template

> Copy-paste this when you start a new package, or when an existing
> package's README is too thin. Keeping the shape consistent across
> the workspace is a small thing that pays off — newcomers learn the
> layout once and can navigate any package.

The template is short on purpose. Add subsections only when you have
something concrete to say in them.

---

```markdown
# <package_name>

> One-sentence summary in italics. What does this package do, and who
> for? If a reader stops here, the rest should be a sensible fallback.

**Status:** ✅ shipping ‖ 🟡 stub ‖ 🔴 planned — pick one and link to the
issue tracker label that owns the next milestone.

## Hardware

What hardware (if any) does this package need? "Either Mini or Max" is a
fine answer for most things; sensor wrappers should be specific.

## Topics & services

Two compact tables — one for things this package consumes, one for
things it produces. Reference [`docs/api.md`](./api.md) for
shape definitions; do NOT redeclare them here.

| Direction | Topic | Type | Rate or trigger |
|---|---|---|---|
| sub | `/foo` | `geometry_msgs/Twist` | ~20 Hz |
| pub | `/bar` | `std_msgs/Bool` | latched |

| Service | Type | Server / caller |
|---|---|---|

## Run

```bash
ros2 launch <pkg> <name>.launch.py
```

One concrete command. If there are useful launch arguments, put one or
two example overrides in here.

## Configuration

YAML files (if any) — what to override and when. Cite the file paths so
the operator can read them in-tree.

## Tests

If `test/` has unit tests, link to them and say what they cover at a
high level (one sentence). If there are no tests yet, leave this
section out — don't apologize for it.

## Upstream

External projects this package depends on, with one-line license
notes. Vendor SDKs go here too. **Do not** mention competitor or
inspiration projects — those are off-limits per project policy.

## Related packages

What does this package compose with? List 2–3 related packages with
one-line "this is why you'd reach for both" notes.
```

## Style notes

- **Headings.** Keep them short (one or two words). The file is read
  with grep more often than top-down.
- **Tables over prose.** Topics, services, parameters, env vars — all
  tabular. Easier to skim, easier to diff.
- **No emoji except status badges.** Status emoji are load-bearing
  ("🟡 stub" vs "✅ v0.1"); sprinkling 🚀 and 🎯 elsewhere makes the
  doc harder to read quickly.
- **Cite, don't duplicate.** If a contract is in `docs/api.md`, link
  to it. If a config schema is in another file, link to it. Drift
  between two declarations of the same thing is a future bug.
- **First line is the elevator pitch.** Italicize it (Markdown `>`).
  The package's `package.xml` description is usually the same
  sentence.

## Checking for drift

`ci/check-readme-shape.sh` (planned for Phase 2) will lint READMEs
against this template — same headings, same first-line shape, no
"TODO: package description" placeholders.

Until that lands, `find src -name 'README.md' -exec head -3 {} +`
gives you a quick visual scan.
