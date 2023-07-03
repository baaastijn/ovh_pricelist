# Changelog
All notable changes to this project will be documented in this file.

## [2.1.0] - 2023-07-03
- Removed php dependencies (reduced RAM usage from 7GB ram to 1MB and cpu to 0)
- Removed google fonts
- Added nginx docker container
- Added daily python job in container
- Upload Gzipped json file in S3 (reduced size of json by 30)

## [2.0.0] - 2023-03-15
### Added
- support of Eco ranges (Kimsufi, SoYouStart)
- Pagination to 2000 items for 1 page view

### Changed
- No more datacenter availability. it was adding too many lines

### Fixed
- links to the "buy" webpages redirecting to parent website page
- Sorting by numeric fields now working (price and co)


## [1.0.0] - 2021-05-04
### Added
- support of HIGH-GRADE range
- support of SCALE Range
- Pagination to 600 items for better page load time

### Changed
- No more search option per column. It was not working properly

### Fixed
- links to the "buy" webpages redirecting to relevant URL