# Evolving-sun

Nano agent AI greatly improved

## Security Scanning

This repository has CodeQL security scanning configured to run automatically when source code files are added or modified.

### CodeQL Workflow

The CodeQL workflow (`.github/workflows/codeql.yml`) is configured with path filters to only run when actual source code files are present. This prevents unnecessary workflow failures when only configuration or documentation files are changed.

The workflow will trigger on:
- Push to `main` branch
- Pull requests to `main` branch

Only when files with the following extensions are modified:
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`
- Java/Kotlin: `.java`, `.kt`, `.kts`
- Go: `.go`
- C/C++: `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`
- C#: `.cs`
- Ruby: `.rb`

**Note:** The workflow currently analyzes Python and JavaScript/TypeScript code. To add support for other languages (Java, Go, C++, C#, Ruby), update the `matrix.language` array in `.github/workflows/codeql.yml`.

### Important Note

If you see a "dynamic" CodeQL workflow in the repository settings under **Settings > Code security and analysis > CodeQL analysis**, it should be **disabled** in favor of the custom workflow defined in this repository. The custom workflow provides better control and prevents failures when no source code is present.

To disable the default setup:
1. Go to repository **Settings**
2. Navigate to **Code security and analysis**
3. Under **CodeQL analysis**, click **Disable** or **Remove**

The custom workflow in `.github/workflows/codeql.yml` will handle all CodeQL scanning needs.

## Current Repository Status

This repository currently contains only configuration and security policy files. Once source code is added, the CodeQL workflow will automatically scan it for security vulnerabilities.

## Contributing

Please see [SECURITY.md](SECURITY.md) for information about reporting security vulnerabilities.
