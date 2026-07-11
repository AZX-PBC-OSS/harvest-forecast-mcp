# harvest-forecast-mcp

An [MCP server](https://modelcontextprotocol.io/) for the [Harvest](https://www.getharvest.com/) and [Forecast](https://www.forecastapp.com/) APIs — let AI agents like Claude track time, list projects, and manage assignments and scheduling.

## What it does

`harvest-forecast-mcp` exposes Harvest (time tracking) and Forecast (resource scheduling) operations as [Model Context Protocol](https://modelcontextprotocol.io/) tools. Once configured, an AI agent can:

- **Track time** — list, create, and delete time entries in Harvest
- **Browse projects** — list projects, clients, tasks, and users
- **Manage scheduling** — list and create Forecast assignments, milestones, and holidays

The server speaks stdio MCP, so it drops cleanly into Claude Desktop, Claude Code, or any MCP-compatible client.

## Installation

```bash
# Run instantly without installing (recommended)
uvx harvest-forecast-mcp

# Or install with pip
pip install harvest-forecast-mcp
```

## Configuration

The server reads credentials from environment variables. Harvest and Forecast use separate access tokens and account IDs, so you can configure one or both depending on which tools you need.

| Variable | Required | Description |
| --- | --- | --- |
| `HARVEST_ACCESS_TOKEN` | Harvest tools | Personal access token for the Harvest API |
| `HARVEST_ACCOUNT_ID` | Harvest tools | Harvest account ID (numeric) |
| `FORECAST_ACCESS_TOKEN` | Forecast tools | Personal access token for the Forecast API |
| `FORECAST_ACCOUNT_ID` | Forecast tools | Forecast account ID (numeric) |
| `HARVEST_USER_AGENT` | Yes | Identifying string for API requests (e.g. `your-app (you@example.com)`) |

> **Tip:** Harvest requires a descriptive `User-Agent` header. Set `HARVEST_USER_AGENT` to your app name and contact email.

### Claude Desktop configuration

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "harvest-forecast": {
      "command": "uvx",
      "args": ["harvest-forecast-mcp"],
      "env": {
        "HARVEST_ACCESS_TOKEN": "your-harvest-token",
        "HARVEST_ACCOUNT_ID": "123456",
        "FORECAST_ACCESS_TOKEN": "your-forecast-token",
        "FORECAST_ACCOUNT_ID": "123456",
        "HARVEST_USER_AGENT": "my-claude-agent (you@example.com)"
      }
    }
  }
}
```

## Tools

The server exposes 28 tools across the Harvest and Forecast APIs, including cross-API combinations:

### Harvest — time tracking & project management

| Tool | Description |
| --- | --- |
| `list_harvest_projects` | List all projects with client info, optionally filtered by active status |
| `list_harvest_users` | List all users, optionally filtered by active status |
| `list_harvest_clients` | List all clients, optionally filtered by active status |
| `list_harvest_tasks` | List all tasks available for time tracking |
| `list_time_entries` | List time entries filtered by user, project, and date range (defaults to last 30 days) |
| `create_time_entry` | Log hours against a project + task with optional notes |
| `list_project_assignments` | List users assigned to a Harvest project with rates and budgets |
| `harvest_whoami` | Get the current authenticated Harvest user's identity and permissions |

### Forecast — scheduling & staffing

| Tool | Description |
| --- | --- |
| `list_forecast_projects` | List all Forecast projects (for scheduling) |
| `list_forecast_people` | List all schedulable people with roles and teams |
| `list_forecast_placeholders` | List all placeholders (role-based slots) |
| `list_forecast_roles` | List all roles with their assigned people and placeholders |
| `list_forecast_milestones` | List all milestones across all projects |
| `get_forecast_project` | Get details for a single Forecast project by ID |
| `get_forecast_person` | Get details for a single Forecast person by ID |
| `list_assignments` | List scheduled assignments filtered by date range, project, or person |
| `create_assignment` | Schedule a person on a project with allocation and dates |
| `update_assignment` | Update an existing assignment |
| `delete_assignment` | Delete an assignment |
| `get_remaining_budgeted_hours` | Get remaining budgeted hours for all projects |
| `get_future_scheduled_hours` | Get future scheduled hours from a date |
| `get_future_scheduled_hours_for_project` | Same, filtered to a single project |
| `get_assigned_people` | Get a mapping of project IDs to assigned person IDs |
| `get_project_heatmap` | Scheduling load heatmap for a project |
| `get_person_heatmap` | Scheduling load heatmap for a person |
| `get_placeholder_heatmap` | Scheduling load heatmap for a placeholder |
| `forecast_whoami` | Get current Forecast user identity and account IDs |

### Cross-API — manager insights

| Tool | Description |
| --- | --- |
| `person_schedule` | A person's complete schedule: Forecast assignments + Harvest time entries for the period |
| `project_overview` | Comprehensive project view: Harvest details + Forecast project + budget + recent time entries |
| `team_utilization` | Scheduled hours (Forecast) vs logged hours (Harvest) per person, with utilization % |
| `who_is_available` | Find people with capacity (not fully scheduled) in a date range |
| `time_summary` | Summarize time entries grouped by project, user, or client |
| `budget_status` | Budget burn-down: remaining budgeted hours vs logged hours last 30 days per project |
| `all_projects_schedule` | Per-project scheduling overview: people, assignments, milestones for a date range |

## Development

```bash
# Install dependencies
uv sync --group dev

# Run tests
uv run pytest

# Type check
uv run pyright src/harvest_forecast_mcp

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development guidelines.

## License

MIT

## Disclaimer

This project is unofficial and not affiliated with, endorsed by, or sponsored by Harvest Inc. or its subsidiaries. "Harvest" and "Forecast" are trademarks of their respective owners. This software is provided "as-is", without any warranty express or implied.

[MIT](LICENSE) — Copyright (c) 2025 AZX, PBC.
