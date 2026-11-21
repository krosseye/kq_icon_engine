# CHANGELOG

<!-- version list -->

## v0.1.2 (2026-11-21)

### Bug Fixes

- Depend on pyside6-essentials instead of full pyside6
  ([`d5a1f4a`](https://github.com/krosseye/kq_icon_engine/commit/d5a1f4ade21cecc546141e08b4a6d6b4d0a3ac1c))

- Keep icon aspect ratio at non-square sizes
  ([`17868a0`](https://github.com/krosseye/kq_icon_engine/commit/17868a0e1d63135d5449e08f5eb394868b379443))

- Ship a PyInstaller hook so bundled icons are included
  ([`5e62832`](https://github.com/krosseye/kq_icon_engine/commit/5e6283246c5362134c31f1a2320d9065db23c979))

### Build System

- Declare all licence files and project URLs
  ([`9248cd7`](https://github.com/krosseye/kq_icon_engine/commit/9248cd7494322edeb494be0ee779a03f7543b2df))

### Chores

- Drop settings that repeat tool defaults
  ([`1ad0dfb`](https://github.com/krosseye/kq_icon_engine/commit/1ad0dfb141761a0338bb597f30fd5f783c5568e1))

- **deps-dev**: Update uv-build requirement
  ([`07dedd2`](https://github.com/krosseye/kq_icon_engine/commit/07dedd261ec2d86d0abc0649c04c22795ae1b3d9))

### Continuous Integration

- Bump actions/checkout from 5 to 7
  ([`00db7ff`](https://github.com/krosseye/kq_icon_engine/commit/00db7ff2a3267d59556227c78f1a6df8ba0b9198))

- Bump actions/setup-python from 6 to 7
  ([`9419169`](https://github.com/krosseye/kq_icon_engine/commit/9419169514c28d5f6fe2e514909dd315aa9b3a9d))

- Bump astral-sh/setup-uv from 6 to 7
  ([`33c496c`](https://github.com/krosseye/kq_icon_engine/commit/33c496c96d3780859dca967df209b0c7d82ca931))

- Commit uv.lock and install locked dependencies
  ([`ba92f80`](https://github.com/krosseye/kq_icon_engine/commit/ba92f80a1913f724a354dfe9bcaec505e8b15ec9))

- Freeze and run a smoke app with PyInstaller
  ([`f99f39b`](https://github.com/krosseye/kq_icon_engine/commit/f99f39b9f19de99b05fd00261e3443ccf261919f))

- Let setup-uv install Python
  ([`4fbc0a1`](https://github.com/krosseye/kq_icon_engine/commit/4fbc0a1d36509378907a70cfdaf1bfb5a3e27619))

- Run ruff and mypy hooks from the project environment
  ([`732a89a`](https://github.com/krosseye/kq_icon_engine/commit/732a89ad1783d0b62359a12d0a08917541a5c18f))

- Tweak workflow timings
  ([`73dd7ad`](https://github.com/krosseye/kq_icon_engine/commit/73dd7add8cbce5fd832d361ff2b9a7a9d109af52))

### Documentation

- Fix license bundling
  ([`1df90f0`](https://github.com/krosseye/kq_icon_engine/commit/1df90f087e95c3ebfe5c1561d999b89802627c33))

- Remove tests badge (build and release run tests)
  ([`56f6473`](https://github.com/krosseye/kq_icon_engine/commit/56f6473d8b8ebc037f19bbea243117594ee31fb6))

### Testing

- Add test suite
  ([`6eec83c`](https://github.com/krosseye/kq_icon_engine/commit/6eec83cd5d97a13abc90d0b0d4b056fdf65652a2))


## v0.1.1 (2026-11-07)

### Bug Fixes

- Cache growing without limit, and consistent name lookup
  ([`80c6a83`](https://github.com/krosseye/kq_icon_engine/commit/80c6a831241e9a949446db9696ac7c559bc66318))

### Continuous Integration

- Skip build and publish when no new version is released
  ([`8a36be9`](https://github.com/krosseye/kq_icon_engine/commit/8a36be93e4712103c5042d991c0383b6be5f0488))


## v0.1.0 (2026-11-07)

- Initial Release
