# srex
Simple Remote EXecution tool

## Minimal usage

Create a `tasks.yaml` file:

```yaml
- action: shell
  name: show hostname
  command: hostname

- action: fetch
  name: fetch release info
  src: /etc/os-release
  dst: ./os-release
```

Run it against an SSH host:

```bash
uv run srex run --hosts user@127.0.0.1:22 --tasks tasks.yaml
```

Hosts can also be loaded from JSON or YAML with `--hosts @hosts.yaml`.
