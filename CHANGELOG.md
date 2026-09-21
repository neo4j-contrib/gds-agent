# Changelog - [1.2.0] - yyyy-mm-dd


### Breaking Changes

### New Features

### Bug Fixes
1. Update mcp dependency to 2.0.
2. Remove the stale example requirements file that was only example `import_data.py`
3. Use exact node identifier matching and allow numeric identifier inputs across graph algorithms.
4. Update SKILL.md to always create session before graph projection for session mode.
5. Document empty similarity filters as unfiltered, improve truncation warnings and skill troubleshooting.
6. Changed `failIfMissing=True` in `drop_graph` as otherwise the function throws an uninformative `'NoneType' object has no attribute 'get'` `error instead.
