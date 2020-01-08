# Changelog

## [1.4.0] - 2020-01-08

### Added
- Added the ability to allow certain fields through even when `throw_on_unhandled` is set.
- Added `@constructed` decorator which takes a function which will be called with any newly created instance.

## [1.3.0] - 2020-01-08

### Changed
- `ClassVar`s are now ignored when deserializing

## [1.2.0] - 2019-12-18

### Added
- Added ability to specify a default value for missing fields in the data using the `default` decorator.

### Fixed
- Fixed debug name for dictionary attributes for exceptions

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
