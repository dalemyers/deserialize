# Changelog

## [1.7.0] - ?

### Added
- Added support for fallback to dict for unsupported types when downcasting

## [1.6.1] - 2020-06-04

### Fixed
- Fixed the bug introduced in 1.6.0 which accidentally left the downcasts as the base class

## [1.6.0] - 2020-06-04

### Added
- Added support for more than 1 level of subclass for when downcasting

## [1.5.1] - 2020-01-16

### Fixed
- Some exceptions weren't tracking the debug name

## [1.5.0] - 2020-01-15

### Added
- Added ability to specify downcasts based on a field value in the data

## [1.4.1] - 2020-01-08

### Fixed
- Fixed issue where unhandled fields were not recorded correctly when field and property names differ

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
