# Changelog

All notable changes to SuperDiagnosticTool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-01-25

### Fixed
- **CRITICAL:** API key not persisting between program sessions
  - Removed over-aggressive regex sanitization that was corrupting keys
  - Added UTF-8 encoding to prevent character corruption
  - Improved error messages for better debugging

### Changed
- API key input now shows characters (visible input) to support Ctrl+V paste
- Enhanced file I/O operations with explicit UTF-8 encoding
- Better error handling with informative user messages

### Technical
- Replaced `re.sub(r'[^a-zA-Z0-9\-\._]', '', key)` with simple `.strip()`
- Added `encoding="utf-8"` parameter to all `open()` calls
- Replaced silent `except: pass` with proper exception handling

---

## [1.0.0] - 2026-01-24

### Added
- Initial production release
- AI-powered system diagnostics using Google Gemini 2.5 Flash
- Universal hardware support (1-128+ CPU cores)
- Automated PowerShell remediation scripts
- Professional HTML reports with dark theme
- Security-first architecture with 6-layer validation
- Automatic system restore point creation
- Custom diagnostic icon with "Pulse" design
- Comprehensive system scanning:
  - CPU, RAM, Disk health
  - Network diagnostics
  - Security integrity checks
  - Event log analysis
  - Bluetooth status
  - GPU information
  - Startup applications
  - Failed services detection

### Security
- Multi-level script validation before execution
- Dry-run simulation mode
- User confirmation required for all changes
- System restore point integration
- Monitored execution with change detection

---

## Release Types

- **Major (X.0.0):** Breaking changes, major new features
- **Minor (1.X.0):** New features, backward compatible
- **Patch (1.0.X):** Bug fixes, security patches

---

[1.0.1]: https://github.com/Guettaf-hossam/SuperDiagnosticTool/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/tag/v1.0.0
