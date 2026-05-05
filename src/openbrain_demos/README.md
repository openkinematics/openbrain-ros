# openbrain_demos

> The OpenBrain demo catalog — one folder per demo. This README is the
> single source of truth for the slugs, statuses, and categories that the
> marketing site at [openkinematics.com/demos](https://www.openkinematics.com/demos)
> and the dashboard's demo gallery both link into.

| Slug | Category | Hardware | Status |
|---|---|---|---|
| [`cockpit`](cockpit) | Teleop | Either | 🟢 Phase 1 |
| [`health`](health) | System | Either | 🟢 Phase 1 |
| [`missions`](missions) | Navigation | Either | 🟢 Phase 1 |
| [`profile`](profile) | System | Either | 🟢 Phase 1 |
| [`fleet-control`](fleet-control) | Fleet | Max | 🟢 Phase 1 |
| [`yolo-perception`](yolo-perception) | Perception | Either | 🟢 Phase 1 |
| [`vslam-gps-denied`](vslam-gps-denied) | Navigation | Either | 🟢 Phase 1 |
| [`quadruped-patrol`](quadruped-patrol) | Navigation | Either | 🟢 Phase 1 |
| [`my-ui`](my-ui) | Dashboard | Either | 🟡 stub |
| [`groot-vla-pick-place`](groot-vla-pick-place) | VLA | Max | 🟡 stub |
| [`openvla-grasp`](openvla-grasp) | VLA | Max | 🟡 stub |
| [`diffusion-policy`](diffusion-policy) | Manipulation | Max | 🟡 stub |
| [`lerobot-act`](lerobot-act) | Manipulation | Either | 🟡 stub |
| [`nvblox-mapping`](nvblox-mapping) | Navigation | Max | 🟡 stub |
| [`rememb-r-navigation`](rememb-r-navigation) | Navigation | Max | 🟡 stub |
| [`rosa-voice-control`](rosa-voice-control) | Teleop | Max | 🟡 stub |
| [`humanoid-locomotion`](humanoid-locomotion) | Locomotion | Max | 🟡 stub |
| [`warehouse-pick`](warehouse-pick) | Manipulation | Max | 🟡 stub |
| [`edge-nerf`](edge-nerf) | Perception | Max | 🟡 stub |
| [`vlm-isaac-sim`](vlm-isaac-sim) | VLA | Max | 🟡 stub |

🟢 = real implementation in v0.1 (8 demos) · 🟡 = stub package, scaffolded with rich README + acceptance checklist (12 demos)

## Anatomy of a demo package

```
src/openbrain_demos/<slug>/
├── package.xml                 # ament_python or ament_cmake
├── setup.py                    # if python; or CMakeLists.txt if C++
├── launch/
│   └── <slug>.launch.py
├── config/                     # YAML params if needed
├── <slug>/                     # Python module / C++ src
└── README.md                   # what it does, hardware needed, run instructions
```

Use the [package README template](../../docs/package-readme-template.md) as
the starting point.

## Graduating a stub

When a stub becomes a real implementation:

1. Replace the placeholder `launch/<slug>.launch.py` with the real launch composition.
2. Add the implementation under `<slug>/` (or `src/` for C++).
3. Add at least one unit test under `test/`.
4. Update the demo's own `README.md` with real run instructions and any new params.
5. Flip the status in this README's table from 🟡 to 🟢.
6. Open a PR — the marketing site picks up the new status from the next site
   build (see [openkinematics.com/demos](https://www.openkinematics.com/demos)).

See [`CONTRIBUTING.md`](../../CONTRIBUTING.md#adding-a-new-demo) for the
full contribution flow.
