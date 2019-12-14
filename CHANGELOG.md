# Changelog

## [1.1.0] - 2019-12-14

### Added
- Ability to throw an exception on unhandled fields
- Ability to deserialize to types which have a constructor specified
- Support for storing raw data on the deserialized object

### Changed
- Simplified error messages when comparing against None types
- Added better error messages for union deserialization failures
- Now does explicit checks for attributes before using them instead of try-except to make debugging easier (fewer exceptions raised)


## [1.0.0] - 2019-10-07

Initial release
