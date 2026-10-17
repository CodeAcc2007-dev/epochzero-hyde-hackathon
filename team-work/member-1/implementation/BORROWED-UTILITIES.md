# Utility reuse

Unchanged public Context and race helpers are copied from the verified Member 3 implementation through Member 4's source. `SpatialContext.spatial_plans` is the unchanged city/expansion geometry method from Member 4 RouteContext, without its macro plans, sampled opponent policy or mean-time math. New goal policy and integer-goal helper are separate. No environment or frozen bot was changed.

- `team-work/member-3/bots/B05/v003/member3_core.py`: SHA-256 `4fdabf1b1bb282a225701b8078b9135dc26e0622fc25e1ed9fd516bf56a6b4bd`.
- `team-work/member-4/implementation/member4_policies.py`: SHA-256 `703565d7d77156eb0b48fb9bbad54e56f2d53a9ec8c82c3ec0dd86f673294e9b`.
