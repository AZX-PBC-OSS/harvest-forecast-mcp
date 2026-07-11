"""MCP server for Harvest and Forecast APIs.

Exposes tools for AI agents to track time, list projects, manage assignments,
and query scheduling aggregates via the Harvest and Forecast APIs.
"""

import json
import os
from datetime import date, timedelta
from typing import Any

from harvest_forecast import (
    AssignmentFilter,
    AssignmentRequest,
    ForecastHTTPError,
    RetryPolicy,
    SyncForecastClient,
)
from harvest_forecast._harvest.client import SyncHarvestClient
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("harvest-forecast")


def _get_config() -> dict[str, str]:
    """Read required env vars, raising with a clear message if any are missing."""
    required = [
        "HARVEST_ACCESS_TOKEN",
        "HARVEST_ACCOUNT_ID",
        "FORECAST_ACCESS_TOKEN",
        "FORECAST_ACCOUNT_ID",
        "HARVEST_USER_AGENT",
    ]
    config: dict[str, str] = {}
    missing: list[str] = []
    for key in required:
        val = os.environ.get(key)
        if not val:
            missing.append(key)
        else:
            config[key] = val
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set them in your MCP client config or .env file."
        )
    return config


def _harvest_client() -> SyncHarvestClient:
    """Create a SyncHarvestClient from env vars."""
    c = _get_config()
    return SyncHarvestClient(
        access_token=c["HARVEST_ACCESS_TOKEN"],
        account_id=c["HARVEST_ACCOUNT_ID"],
        user_agent=c["HARVEST_USER_AGENT"],
        retry=RetryPolicy.fast_test(max_attempts=3),
    )


def _forecast_client() -> SyncForecastClient:
    """Create a SyncForecastClient from env vars."""
    c = _get_config()
    return SyncForecastClient(
        access_token=c["FORECAST_ACCESS_TOKEN"],
        account_id=c["FORECAST_ACCOUNT_ID"],
        user_agent=c["HARVEST_USER_AGENT"],
        retry=RetryPolicy.fast_test(max_attempts=3),
    )


def _format_error(exc: ForecastHTTPError) -> str:
    """Format a ForecastHTTPError as a human-readable error string."""
    body = exc.response_body[:500] if exc.response_body else "No details"
    return f"Error {exc.status_code}: {body}"


def _serialize(obj: Any) -> str:
    """Serialize a Pydantic model or list of models to JSON string."""
    if isinstance(obj, list):
        return json.dumps(
            [item.model_dump() if hasattr(item, "model_dump") else item for item in obj],
            default=str,
            indent=2,
        )
    if hasattr(obj, "model_dump"):
        return json.dumps(obj.model_dump(), default=str, indent=2)
    return str(obj)


# ---------- Harvest tools ----------


@mcp.tool()
def list_harvest_projects(is_active: bool | None = None) -> str:
    """List all projects in Harvest with client information.

    Args:
        is_active: If True, only return active projects. If False, only archived.
    """
    try:
        with _harvest_client() as client:
            projects = client.list_projects(is_active=is_active)
        return _serialize(projects)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_harvest_users(is_active: bool | None = None) -> str:
    """List all users in Harvest.

    Args:
        is_active: If True, only return active users.
    """
    try:
        with _harvest_client() as client:
            users = client.list_users(is_active=is_active)
        return _serialize(users)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_harvest_clients(is_active: bool | None = None) -> str:
    """List all clients in Harvest.

    Args:
        is_active: If True, only return active clients.
    """
    try:
        with _harvest_client() as client:
            clients = client.list_clients(is_active=is_active)
        return _serialize(clients)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_harvest_tasks(is_active: bool | None = None) -> str:
    """List all tasks available for time tracking in Harvest.

    Args:
        is_active: If True, only return active tasks.
    """
    try:
        with _harvest_client() as client:
            tasks = client.list_tasks(is_active=is_active)
        return _serialize(tasks)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_time_entries(
    user_id: int | None = None,
    project_id: int | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> str:
    """List time entries from Harvest, optionally filtered by user, project, and date range.

    Args:
        user_id: Filter to a specific user's entries.
        project_id: Filter to a specific project's entries.
        from_date: Start date (YYYY-MM-DD). Defaults to 30 days ago.
        to_date: End date (YYYY-MM-DD). Defaults to today.
    """
    today = date.today()
    from_str = from_date or (today - timedelta(days=30)).isoformat()
    to_str = to_date or today.isoformat()
    try:
        with _harvest_client() as client:
            entries = client.list_time_entries(
                user_id=user_id,
                project_id=project_id,
                from_date=from_str,
                to_date=to_str,
            )
        return _serialize(entries)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def create_time_entry(
    project_id: int,
    task_id: int,
    spent_date: str,
    hours: float,
    notes: str | None = None,
) -> str:
    """Log time against a Harvest project and task.

    Args:
        project_id: Harvest project ID.
        task_id: Harvest task ID.
        spent_date: Date the time was spent (YYYY-MM-DD).
        hours: Number of hours to log (can be decimal, e.g. 1.5).
        notes: Optional notes for the time entry.
    """
    try:
        with _harvest_client() as client:
            entry = client.create_time_entry(
                project_id=project_id,
                task_id=task_id,
                spent_date=spent_date,
                hours=hours,
                notes=notes,
            )
        return _serialize(entry)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_project_assignments(project_id: int) -> str:
    """List users assigned to a Harvest project with their rates and budgets.

    Args:
        project_id: Harvest project ID.
    """
    try:
        with _harvest_client() as client:
            assignments = client.list_user_assignments(project_id)
        return _serialize(assignments)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def harvest_whoami() -> str:
    """Get the current authenticated Harvest user's identity and permissions."""
    try:
        with _harvest_client() as client:
            user = client.whoami()
        return _serialize(user)
    except ForecastHTTPError as exc:
        return _format_error(exc)


# ---------- Forecast tools ----------


@mcp.tool()
def list_forecast_projects() -> str:
    """List all projects in Forecast (for scheduling purposes)."""
    try:
        with _forecast_client() as client:
            projects = client.list_projects()
        return _serialize(projects)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_forecast_people() -> str:
    """List all people being scheduled in Forecast, with their roles and teams."""
    try:
        with _forecast_client() as client:
            people = client.list_people()
        return _serialize(people)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_assignments(
    start_date: str,
    end_date: str,
    project_id: int | None = None,
    person_id: int | None = None,
) -> str:
    """List scheduled assignments in Forecast within a date range.

    Args:
        start_date: Start of date range (YYYY-MM-DD). Required.
        end_date: End of date range (YYYY-MM-DD). Required.
        project_id: Filter to assignments for a specific project.
        person_id: Filter to assignments for a specific person.
    """
    try:
        with _forecast_client() as client:
            assignments = client.list_assignments(
                AssignmentFilter(
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date),
                    project_id=project_id,
                    person_id=person_id,
                )
            )
        return _serialize(assignments)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def create_assignment(
    project_id: int,
    person_id: int,
    start_date: str,
    end_date: str,
    allocation: int | None = None,
    notes: str | None = None,
) -> str:
    """Schedule a person on a Forecast project.

    Args:
        project_id: Forecast project ID (must be >= 1).
        person_id: Forecast person ID (0 = Everyone).
        start_date: Assignment start date (YYYY-MM-DD).
        end_date: Assignment end date (YYYY-MM-DD).
        allocation: Allocation in minutes per day (e.g. 480 = 8 hours).
        notes: Optional notes for the assignment.
    """
    try:
        with _forecast_client() as client:
            assignment = client.create_assignment(
                AssignmentRequest(
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date),
                    project_id=project_id,
                    person_id=person_id,
                    allocation=allocation,
                    notes=notes,
                )
            )
        return _serialize(assignment)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def update_assignment(
    assignment_id: int,
    project_id: int,
    person_id: int,
    start_date: str,
    end_date: str,
    allocation: int | None = None,
    notes: str | None = None,
) -> str:
    """Update an existing Forecast assignment.

    Args:
        assignment_id: ID of the assignment to update (must be >= 1).
        project_id: Forecast project ID (must be >= 1).
        person_id: Forecast person ID.
        start_date: New start date (YYYY-MM-DD).
        end_date: New end date (YYYY-MM-DD).
        allocation: New allocation in minutes per day.
        notes: New notes.
    """
    try:
        with _forecast_client() as client:
            assignment = client.update_assignment(
                assignment_id,
                AssignmentRequest(
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date),
                    project_id=project_id,
                    person_id=person_id,
                    allocation=allocation,
                    notes=notes,
                ),
            )
        return _serialize(assignment)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def delete_assignment(assignment_id: int) -> str:
    """Delete a Forecast assignment.

    Args:
        assignment_id: ID of the assignment to delete (must be >= 1).
    """
    try:
        with _forecast_client() as client:
            client.delete_assignment(assignment_id)
        return f"Assignment {assignment_id} deleted."
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_remaining_budgeted_hours() -> str:
    """Get remaining budgeted hours for all Forecast projects."""
    try:
        with _forecast_client() as client:
            items = client.remaining_budgeted_hours()
        return _serialize(items)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_future_scheduled_hours(from_date: str) -> str:
    """Get future scheduled hours for all projects starting from a date.

    Args:
        from_date: Starting date (YYYY-MM-DD).
    """
    try:
        with _forecast_client() as client:
            items = client.future_scheduled_hours(from_date)
        return _serialize(items)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_project_heatmap(
    project_id: int,
    from_date: str,
    to_date: str,
    scale: str = "daily",
) -> str:
    """Get a scheduling heatmap for a Forecast project.

    Args:
        project_id: Forecast project ID.
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        scale: Time scale — "daily" or "weekly".
    """
    try:
        with _forecast_client() as client:
            items = client.project_heatmap(from_date, to_date, project_id, scale)
        return _serialize(items)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_person_heatmap(
    person_id: int,
    from_date: str,
    to_date: str,
    scale: str = "daily",
) -> str:
    """Get a scheduling heatmap for a Forecast person.

    Args:
        person_id: Forecast person ID.
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        scale: Time scale — "daily" or "weekly".
    """
    try:
        with _forecast_client() as client:
            items = client.person_heatmap(from_date, to_date, person_id, scale)
        return _serialize(items)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def forecast_whoami() -> str:
    """Get the current Forecast user's identity and account IDs."""
    try:
        with _forecast_client() as client:
            user = client.whoami()
        return _serialize(user)
    except ForecastHTTPError as exc:
        return _format_error(exc)


# ---------- Forecast: additional endpoints ----------


@mcp.tool()
def list_forecast_milestones() -> str:
    """List all milestones across all Forecast projects."""
    try:
        with _forecast_client() as client:
            milestones = client.list_milestones()
        return _serialize(milestones)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_forecast_placeholders() -> str:
    """List all placeholders (unnamed/role-based slots) available for scheduling in Forecast."""
    try:
        with _forecast_client() as client:
            placeholders = client.list_placeholders()
        return _serialize(placeholders)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def list_forecast_roles() -> str:
    """List all roles defined in Forecast, with their assigned people and placeholders."""
    try:
        with _forecast_client() as client:
            roles = client.list_roles()
        return _serialize(roles)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_forecast_project(project_id: int) -> str:
    """Get details for a single Forecast project by ID.

    Args:
        project_id: Forecast project ID.
    """
    try:
        with _forecast_client() as client:
            project = client.get_project(project_id)
        return _serialize(project)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_forecast_person(person_id: int) -> str:
    """Get details for a single Forecast person by ID.

    Args:
        person_id: Forecast person ID.
    """
    try:
        with _forecast_client() as client:
            person = client.get_person(person_id)
        return _serialize(person)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_future_scheduled_hours_for_project(from_date: str, project_id: int) -> str:
    """Get future scheduled hours for a specific Forecast project.

    Args:
        from_date: Starting date (YYYY-MM-DD).
        project_id: Forecast project ID.
    """
    try:
        with _forecast_client() as client:
            items = client.future_scheduled_hours_for_project(from_date, project_id)
        return _serialize(items)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_assigned_people(start_date: str, end_date: str) -> str:
    """Get a mapping of Forecast project IDs to the person IDs assigned to each.

    Args:
        start_date: Start of date range (YYYY-MM-DD).
        end_date: End of date range (YYYY-MM-DD).
    """
    try:
        with _forecast_client() as client:
            mapping = client.assigned_people(start_date, end_date)
        return json.dumps(mapping, indent=2)
    except ForecastHTTPError as exc:
        return _format_error(exc)


@mcp.tool()
def get_placeholder_heatmap(
    placeholder_id: int,
    from_date: str,
    to_date: str,
    scale: str = "daily",
) -> str:
    """Get a scheduling heatmap for a Forecast placeholder.

    Args:
        placeholder_id: Forecast placeholder ID.
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        scale: Time scale — "daily" or "weekly".
    """
    try:
        with _forecast_client() as client:
            items = client.placeholder_heatmap(from_date, to_date, placeholder_id, scale)
        return _serialize(items)
    except ForecastHTTPError as exc:
        return _format_error(exc)


# ---------- Cross-API combination tools ----------


@mcp.tool()
def person_schedule(
    person_id: int,
    start_date: str,
    end_date: str,
) -> str:
    """Get a person's complete schedule: Forecast assignments + Harvest time entries for the period.

    Combines both APIs to show what a person is scheduled to work on (Forecast)
    and what they've actually logged (Harvest) in one view.

    Args:
        person_id: Forecast person ID (for assignments) — also used to look up
            the corresponding Harvest user if the person has a harvest_user_id.
        start_date: Start of date range (YYYY-MM-DD).
        end_date: End of date range (YYYY-MM-DD).
    """
    result: dict[str, Any] = {"assignments": [], "time_entries": []}
    person: Any = None
    try:
        with _forecast_client() as fc:
            person = fc.get_person(person_id)
            result["person"] = person.model_dump()
            assignments = fc.list_assignments(
                AssignmentFilter(
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date),
                    person_id=person_id,
                )
            )
            result["assignments"] = [a.model_dump() for a in assignments]
    except ForecastHTTPError as exc:
        result["forecast_error"] = _format_error(exc)

    try:
        with _harvest_client() as hc:
            harvest_user_id = person.harvest_user_id if person else None
            if harvest_user_id:
                entries = hc.list_time_entries(
                    user_id=harvest_user_id,
                    from_date=start_date,
                    to_date=end_date,
                )
                result["time_entries"] = [e.model_dump() for e in entries]
            else:
                result["time_entries"] = "No linked Harvest user — cannot fetch time entries."
    except ForecastHTTPError as exc:
        result["harvest_error"] = _format_error(exc)

    return json.dumps(result, default=str, indent=2)


@mcp.tool()
def project_overview(project_id: int) -> str:
    """Get a comprehensive project overview combining Harvest and Forecast data.

    Returns Harvest project details, Forecast project details (if linked),
    remaining budgeted hours, future scheduled hours, and recent time entries.

    Args:
        project_id: Harvest project ID.
    """
    result: dict[str, Any] = {}

    try:
        with _harvest_client() as hc:
            projects = hc.list_projects()
            hp = next((p for p in projects if p.id == project_id), None)
            if hp:
                result["harvest_project"] = hp.model_dump()
            assignments = hc.list_user_assignments(project_id)
            result["harvest_user_assignments"] = [a.model_dump() for a in assignments]
            entries = hc.list_time_entries(
                project_id=project_id,
                from_date=(date.today() - timedelta(days=30)).isoformat(),
                to_date=date.today().isoformat(),
            )
            result["recent_time_entries"] = [e.model_dump() for e in entries]
    except ForecastHTTPError as exc:
        result["harvest_error"] = _format_error(exc)

    try:
        with _forecast_client() as fc:
            fp_projects = fc.list_projects()
            fp = next((p for p in fp_projects if p.harvest_id == project_id), None)
            if fp:
                result["forecast_project"] = fp.model_dump()
                budgeted = fc.remaining_budgeted_hours()
                budget = next((b for b in budgeted if b.project_id == fp.id), None)
                if budget:
                    result["remaining_budgeted_hours"] = budget.model_dump()
                scheduled = fc.future_scheduled_hours_for_project(date.today().isoformat(), fp.id)
                result["future_scheduled_hours"] = [s.model_dump() for s in scheduled]
    except ForecastHTTPError as exc:
        result["forecast_error"] = _format_error(exc)

    return json.dumps(result, default=str, indent=2)


@mcp.tool()
def team_utilization(
    start_date: str,
    end_date: str,
) -> str:
    """Get team utilization: scheduled hours (Forecast) vs logged hours (Harvest) per person.

    For each Forecast person with a linked Harvest user, shows their total
    scheduled allocation and total logged hours in the date range, with a
    utilization percentage.

    Args:
        start_date: Start of date range (YYYY-MM-DD).
        end_date: End of date range (YYYY-MM-DD).
    """
    result: list[dict[str, Any]] = []

    try:
        with _forecast_client() as fc:
            people = fc.list_people()
            assignments = fc.list_assignments(
                AssignmentFilter(
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date),
                )
            )

        person_assignments: dict[int, list[Any]] = {}
        for a in assignments:
            if a.person_id:
                person_assignments.setdefault(a.person_id, []).append(a)

        with _harvest_client() as hc:
            for person in people:
                if not person.harvest_user_id:
                    continue
                person_asgmts = person_assignments.get(person.id, [])
                scheduled_minutes = sum(a.allocation or 0 for a in person_asgmts)
                scheduled_hours = round(scheduled_minutes / 60, 1)

                try:
                    entries = hc.list_time_entries(
                        user_id=person.harvest_user_id,
                        from_date=start_date,
                        to_date=end_date,
                    )
                    logged_hours = sum(float(e.hours or 0) for e in entries)
                except ForecastHTTPError:
                    logged_hours = 0.0

                utilization = (
                    round((logged_hours / scheduled_hours) * 100, 1)
                    if scheduled_hours > 0
                    else None
                )

                result.append(
                    {
                        "person_id": person.id,
                        "name": f"{person.first_name} {person.last_name}",
                        "harvest_user_id": person.harvest_user_id,
                        "scheduled_hours": scheduled_hours,
                        "logged_hours": round(logged_hours, 1),
                        "utilization_pct": utilization,
                        "assignment_count": len(person_asgmts),
                    }
                )
    except ForecastHTTPError as exc:
        return _format_error(exc)

    return json.dumps(result, default=str, indent=2)


@mcp.tool()
def who_is_available(
    start_date: str,
    end_date: str,
    max_daily_minutes: int = 480,
) -> str:
    """Find people who have capacity (are not fully scheduled) in a date range.

    Lists Forecast people whose total scheduled allocation in the period
    is below the given threshold, so they can take on more work.

    Args:
        start_date: Start of date range (YYYY-MM-DD).
        end_date: End of date range (YYYY-MM-DD).
        max_daily_minutes: Max allocation to be considered "available" (default 480 = 8h/day).
    """
    try:
        with _forecast_client() as fc:
            people = fc.list_people()
            assignments = fc.list_assignments(
                AssignmentFilter(
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date),
                )
            )
    except ForecastHTTPError as exc:
        return _format_error(exc)

    person_totals: dict[int, int] = {}
    for a in assignments:
        if a.person_id:
            person_totals[a.person_id] = person_totals.get(a.person_id, 0) + (a.allocation or 0)

    available: list[dict[str, Any]] = []
    for person in people:
        if person.archived:
            continue
        total = person_totals.get(person.id, 0)
        num_days = max((date.fromisoformat(end_date) - date.fromisoformat(start_date)).days, 1)
        avg_daily = total // num_days
        if avg_daily < max_daily_minutes:
            available.append(
                {
                    "person_id": person.id,
                    "name": f"{person.first_name} {person.last_name}",
                    "roles": person.roles,
                    "teams": person.teams,
                    "total_scheduled_minutes": total,
                    "avg_daily_minutes": avg_daily,
                    "remaining_daily_minutes": max_daily_minutes - avg_daily,
                }
            )

    available.sort(key=lambda p: p["remaining_daily_minutes"], reverse=True)
    return json.dumps(available, default=str, indent=2)


@mcp.tool()
def time_summary(
    from_date: str | None = None,
    to_date: str | None = None,
    group_by: str = "project",
) -> str:
    """Summarize Harvest time entries, grouped by project, user, or client.

    Args:
        from_date: Start date (YYYY-MM-DD). Defaults to 7 days ago.
        to_date: End date (YYYY-MM-DD). Defaults to today.
        group_by: How to group the summary — "project", "user", or "client".
    """
    today = date.today()
    from_str = from_date or (today - timedelta(days=7)).isoformat()
    to_str = to_date or today.isoformat()

    try:
        with _harvest_client() as hc:
            entries = hc.list_time_entries(from_date=from_str, to_date=to_str)
    except ForecastHTTPError as exc:
        return _format_error(exc)

    groups: dict[str, dict[str, float]] = {}
    for entry in entries:
        if group_by == "user":
            key = f"{entry.user.id}: {entry.user.name}"
        elif group_by == "client":
            key = f"{entry.client.id}: {entry.client.name}"
        else:
            key = f"{entry.project.id}: {entry.project.name}"
        hours = float(entry.hours or 0)
        if key not in groups:
            groups[key] = {"hours": 0.0, "entries": 0}
        groups[key]["hours"] += hours
        groups[key]["entries"] += 1

    result: list[dict[str, Any]] = [
        {"name": k, "hours": round(v["hours"], 1), "entries": v["entries"]}
        for k, v in sorted(groups.items(), key=lambda x: x[1]["hours"], reverse=True)
    ]
    total_hours = sum(v["hours"] for v in groups.values())
    return json.dumps(
        {
            "period": {"from": from_str, "to": to_str},
            "total_hours": round(total_hours, 1),
            "groups": result,
        },
        indent=2,
    )


@mcp.tool()
def budget_status() -> str:
    """Get budget burn-down: remaining budgeted hours (Forecast) vs logged hours (Harvest, last 30 days) per project.

    Cross-references Forecast's remaining_budgeted_hours with recent Harvest
    time entries to show which projects are burning through their budget fastest.
    """
    try:
        with _forecast_client() as fc:
            forecast_projects = fc.list_projects()
            budgeted = fc.remaining_budgeted_hours()
    except ForecastHTTPError as exc:
        return _format_error(exc)

    fp_by_id = {p.id: p for p in forecast_projects}
    budget_by_harvest_id: dict[int, Any] = {}
    for b in budgeted:
        fp = fp_by_id.get(b.project_id)
        if fp and fp.harvest_id:
            budget_by_harvest_id[fp.harvest_id] = b.model_dump()

    try:
        with _harvest_client() as hc:
            harvest_projects = hc.list_projects(is_active=True)
            from_str = (date.today() - timedelta(days=30)).isoformat()
            entries = hc.list_time_entries(from_date=from_str)
    except ForecastHTTPError as exc:
        return _format_error(exc)

    logged_by_project: dict[int, float] = {}
    for e in entries:
        logged_by_project[e.project.id] = logged_by_project.get(e.project.id, 0) + float(
            e.hours or 0
        )

    result: list[dict[str, Any]] = []
    for hp in harvest_projects:
        budget = budget_by_harvest_id.get(hp.id)
        logged_30d = round(logged_by_project.get(hp.id, 0), 1)
        result.append(
            {
                "harvest_project_id": hp.id,
                "project_name": hp.name,
                "client": hp.client.name if hp.client else None,
                "remaining_budgeted_hours": budget.get("hours") if budget else None,
                "budget_by": budget.get("budget_by") if budget else None,
                "logged_hours_last_30d": logged_30d,
            }
        )

    return json.dumps(result, default=str, indent=2)


@mcp.tool()
def all_projects_schedule(
    start_date: str,
    end_date: str,
) -> str:
    """Get a scheduling overview for all projects: assignments, assigned people, and milestones.

    Combines Forecast assignments, people, and milestones into a per-project
    view showing who is working on what during the date range.

    Args:
        start_date: Start of date range (YYYY-MM-DD).
        end_date: End of date range (YYYY-MM-DD).
    """
    try:
        with _forecast_client() as fc:
            projects = fc.list_projects()
            people = fc.list_people()
            assignments = fc.list_assignments(
                AssignmentFilter(
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date),
                )
            )
            milestones = fc.list_milestones()
    except ForecastHTTPError as exc:
        return _format_error(exc)

    person_by_id = {p.id: p for p in people}
    assignments_by_project: dict[int, list[Any]] = {}
    for a in assignments:
        if a.project_id:
            assignments_by_project.setdefault(a.project_id, []).append(a)

    milestones_by_project: dict[int, list[Any]] = {}
    for m in milestones:
        if m.project_id:
            milestones_by_project.setdefault(m.project_id, []).append(m)

    result: list[dict[str, Any]] = []
    for project in projects:
        if project.archived:
            continue
        proj_assignments = assignments_by_project.get(project.id, [])
        proj_people: list[dict[str, Any]] = []
        for a in proj_assignments:
            if a.person_id and a.person_id in person_by_id:
                p = person_by_id[a.person_id]
                proj_people.append(
                    {
                        "person_id": p.id,
                        "name": f"{p.first_name} {p.last_name}",
                        "roles": p.roles,
                        "start_date": a.start_date.isoformat() if a.start_date else None,
                        "end_date": a.end_date.isoformat() if a.end_date else None,
                        "allocation": a.allocation,
                    }
                )
            elif a.placeholder_id:
                proj_people.append(
                    {
                        "placeholder_id": a.placeholder_id,
                        "start_date": a.start_date.isoformat() if a.start_date else None,
                        "end_date": a.end_date.isoformat() if a.end_date else None,
                        "allocation": a.allocation,
                    }
                )

        proj_milestones = [
            {"id": m.id, "name": m.name, "date": m.date.isoformat() if m.date else None}
            for m in milestones_by_project.get(project.id, [])
        ]

        result.append(
            {
                "project_id": project.id,
                "name": project.name,
                "code": project.code,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "harvest_id": project.harvest_id,
                "people": proj_people,
                "milestones": proj_milestones,
                "assignment_count": len(proj_assignments),
            }
        )

    return json.dumps(result, default=str, indent=2)


def main() -> None:
    """Run the MCP server with stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
