# Versioning Requirements

## Version Format
- Semantic Versioning: X.Y.Z (Major.Minor.Patch)
- Version is stored in `VERSION` file at project root
- Update version manually before releasing

## Version Bump Rules
- **Major** (X): Incompatible API changes
- **Minor** (Y): New backward-compatible functionality  
- **Patch** (Z): Backward-compatible bug fixes

## Release Process
1. Update VERSION file with new version
2. Commit with message: `Bump version to X.Y.Z`
3. Push to main branch
4. CI will verify version was bumped

## CI Version Check
- On push to main branch, CI verifies VERSION file was modified
- Version must increment from previous release
