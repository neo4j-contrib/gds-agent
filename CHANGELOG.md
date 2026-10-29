# Changelog - [1.2.0] - yyyy-mm-dd


### Breaking Changes

### New Features

### Bug Fixes
1. Warn that truncated results are incomplete and must not drive decisions.
2. Change `failIfMissing=True` in `drop_graph` as otherwise the function throws an uninformative 'NoneType' object has no attribute 'get' error instead.
3. Note that UNDIRECTED degree on an undirectedRelationshipTypes projection counts each neighbor twice.
