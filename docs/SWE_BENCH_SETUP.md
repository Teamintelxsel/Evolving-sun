# SWE-Bench Verified Setup Guide

## Overview

This guide explains how to configure and pin the SWE-Bench Verified Docker image for reproducible benchmark execution.

## Image Pinning Requirements

For reproducible benchmarks, you must pin the SWE-Bench Verified Docker image by its SHA256 digest rather than using a mutable tag like `:verified`.

### Obtaining the Canonical Image Digest

The canonical SWE-Bench Verified image is hosted on GitHub Container Registry (GHCR) at:
```
ghcr.io/princeton-nlp/swe-bench:verified
```

To obtain the current digest:

```bash
# Pull the latest verified image
docker pull ghcr.io/princeton-nlp/swe-bench:verified

# Inspect to get the digest
docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/princeton-nlp/swe-bench:verified
```

This will output something like:
```
ghcr.io/princeton-nlp/swe-bench@sha256:abcdef1234567890...
```

### Configuring tasks.yaml

Once you have the digest, update the `image_digest` field in `tasks.yaml`:

```yaml
suites:
  swebench:
    dataset: "Verified"
    shards: 2
    shard_size: 25
    num_workers: 1
    # Use the full SHA256 digest obtained from docker inspect
    image_digest: "sha256:abcdef1234567890..."  # Replace with actual digest
    timeout: 3600
```

**Important**: The digest format should be `sha256:` followed by the full 64-character hexadecimal hash.

## Why Pin by Digest?

Pinning by digest ensures:

1. **Reproducibility**: The exact same image is used across all runs
2. **Immutability**: The image content cannot change unexpectedly
3. **Provenance**: Clear record of which image version was used
4. **Security**: Protection against tag poisoning or unauthorized updates

## Verification

The benchmark orchestrator (`src/orchestrator/bench_orchestrator.py`) will:

1. Load the image digest from `tasks.yaml`
2. Include it in provenance metadata for all benchmark runs
3. Record it in watermarked result JSONs

You can verify the configuration by running:

```bash
python -c "import yaml; print(yaml.safe_load(open('tasks.yaml'))['suites']['swebench']['image_digest'])"
```

This should output your configured digest.

## References

- [SWE-Bench Official Repository](https://github.com/princeton-nlp/SWE-bench)
- [Docker Image Digests Documentation](https://docs.docker.com/engine/reference/commandline/images/#list-image-digests)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## Troubleshooting

### Cannot Pull Image

If you encounter authentication errors when pulling the image:

```bash
# Authenticate with GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

Replace `USERNAME` with your GitHub username and `$GITHUB_TOKEN` with a GitHub Personal Access Token with `read:packages` scope.

### Empty or Invalid Digest

If the `image_digest` field in `tasks.yaml` is empty or invalid, the orchestrator will:

1. Log a warning about the missing/invalid digest
2. Include the digest value (or lack thereof) in provenance metadata
3. Continue execution (for backward compatibility)

**Best Practice**: Always set a valid digest before running production benchmarks.

### Updating the Digest

When updating to a newer SWE-Bench image:

1. Pull the new image: `docker pull ghcr.io/princeton-nlp/swe-bench:verified`
2. Get the new digest: `docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/princeton-nlp/swe-bench:verified`
3. Update `tasks.yaml` with the new digest
4. Commit the change with a clear message: `git commit -m "Update SWE-Bench image digest to <short-hash>"`
5. Document the reason for the update in your commit message or PR description

## Image Version History

Track digest changes over time for audit purposes:

| Date | Digest (first 12 chars) | Reason for Update | PR/Commit |
|------|------------------------|-------------------|-----------|
| TBD  | sha256:xxxxxx...      | Initial pinning   | TBD       |

Update this table whenever the image digest changes.
