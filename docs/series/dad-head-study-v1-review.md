# Dad head study v1 — visual review record

**Status: not approved.** This is a first technical geometry experiment made with custom Blender Python loft/sweep meshes. It is not hand sculpting and is not a likeness pass that has cleared review.

## Evidence

- [Four-view review board](../../assets/renders/dad-head-study-v1/review-board.png)
- [Front](../../assets/renders/dad-head-study-v1/front.png)
- [Three-quarter](../../assets/renders/dad-head-study-v1/three-quarter.png)
- [Profile](../../assets/renders/dad-head-study-v1/profile.png)
- [Face close-up](../../assets/renders/dad-head-study-v1/face-closeup.png)
- [Editable Blender scene](../../assets/models/dad/studies/dad-head-study-v1.blend)

These are real Blender 5.2.0 WASM / native Cycles outputs. The scene and renders are reproducible via [`tools/blender-wasm-runtime/`](../../tools/blender-wasm-runtime/).

## Observed failures

1. The hair clumps read as isolated spikes, not the broad swept-up sculptural quiff in the face master.
2. The beard reads as a large continuous bib/mask; its cheek line, moustache transition, exposed lip/chin patch, taper and strand flow do not match the master.
3. Eye, nose and ear forms feel detached/over-emphasized rather than integrated into the soft stylized face.
4. The side silhouette and overall face proportions still need measured correction.

Do not use this scene as the starting point for a body, production topology, rig or animation. Do not revive rejected R3/R4 geometry. The next revision should revisit head landmarks and continuous facial/beard/hair surfaces against the approved front, three-quarter, profile and face images before adding detail. The user has not approved any of these results.
