# Dad head study v2 — visual review record

**Status: not approved.** V2 is an exploratory custom-mesh script in Blender Python. The third-party suggestions informed another geometry pass, but the result did not clear visual review. The script is not manual Sculpt Mode work, and the V2 `.blend` is not a clean unified production base mesh.

## Evidence

- [Four-view iPhone-friendly review board](../../assets/renders/dad-head-study-v2/review-board.png)
- [Front](../../assets/renders/dad-head-study-v2/front.png)
- [Three-quarter](../../assets/renders/dad-head-study-v2/three-quarter.png)
- [Profile](../../assets/renders/dad-head-study-v2/profile.png)
- [Face close-up](../../assets/renders/dad-head-study-v2/face-closeup.png)
- [Editable Blender scene](../../assets/models/dad/studies/dad-head-study-v2.blend)
- [Source script](../../tools/blender-wasm-runtime/src/dad_head_study_v2.py)
- [V1 review board](../../assets/renders/dad-head-study-v1/review-board.png)

The images are real Blender 5.2.0 WASM / native Cycles outputs. V2 widens the skull and cheeks, reduces eye size/protrusion, extends the nose bridge/tip and changes the hair to swept custom ribbon meshes. It replaces V1's beard shell with a fitted front-surface patch. These are attempts, not verified likeness features.

## Observed result

1. The broader front shape and smaller eyes are incremental, but the skull still looks helmet-like and the profile remains far from the approved face master.
2. The beard patch reads as a hard, polygonal bib/mask rather than a volume growing from the cheeks and jaw; the moustache/lip transition is unconvincing.
3. The swept hair ribbons still read as repeated triangular spikes rather than the broad, interlocking quiff in the master.
4. The ears and facial forms remain visibly assembled, and the 934 silhouette samples still do not drive the mesh numerically.

The external response's assertion that V1 is already a clean base mesh or "80% success" is not supported by the scene: its meshes are separate surfaces and overlapping components. The suggestion to continue in desktop Blender Sculpt Mode is not being passed to the user as a required action; an interactive sculpt workflow has not been established here. Do not use V1 or V2 for production work. R3/R4 remain rejected.
