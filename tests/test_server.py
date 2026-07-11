import json

import httpx
import pytest
import respx

from harvest_forecast_mcp.server import mcp

HARVEST_BASE = "https://api.harvestapp.com/v2"
FORECAST_BASE = "https://api.forecastapp.com"


async def _call_tool(name: str, args: dict | None = None) -> str:
    content, _ = await mcp.call_tool(name, args or {})
    return content[0].text


# ---------- Harvest tools ----------


@pytest.mark.asyncio
async def test_list_harvest_projects() -> None:
    page = {
        "projects": [
            {
                "id": 1,
                "client": {"id": 10, "name": "Acme"},
                "name": "Alpha",
                "is_active": True,
                "is_billable": True,
                "is_fixed_fee": False,
                "bill_by": "none",
                "budget_by": "none",
                "budget_is_monthly": False,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{HARVEST_BASE}/projects").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool("list_harvest_projects")
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["name"] == "Alpha"


@pytest.mark.asyncio
async def test_list_harvest_users() -> None:
    page = {
        "users": [
            {
                "id": 1,
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "is_active": True,
                "is_contractor": False,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{HARVEST_BASE}/users").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool("list_harvest_users")
    data = json.loads(result)
    assert data[0]["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_list_harvest_clients() -> None:
    page = {
        "clients": [
            {
                "id": 10,
                "name": "Acme",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{HARVEST_BASE}/clients").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool("list_harvest_clients")
    data = json.loads(result)
    assert data[0]["name"] == "Acme"


@pytest.mark.asyncio
async def test_list_harvest_tasks() -> None:
    page = {
        "tasks": [
            {
                "id": 1,
                "name": "Development",
                "billable_by_default": True,
                "is_default": False,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{HARVEST_BASE}/tasks").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool("list_harvest_tasks")
    data = json.loads(result)
    assert data[0]["name"] == "Development"


@pytest.mark.asyncio
async def test_list_time_entries() -> None:
    page = {
        "time_entries": [
            {
                "id": 1,
                "spent_date": "2025-07-01",
                "user": {"id": 1, "name": "Jane Doe"},
                "client": {"id": 10, "name": "Acme"},
                "project": {"id": 1, "name": "Alpha"},
                "task": {"id": 1, "name": "Dev"},
                "hours": "4.0",
                "is_locked": False,
                "is_closed": False,
                "is_billed": False,
                "billable": True,
                "created_at": "2025-07-01T00:00:00Z",
                "updated_at": "2025-07-01T00:00:00Z",
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{HARVEST_BASE}/time_entries").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool(
            "list_time_entries", {"from_date": "2025-07-01", "to_date": "2025-07-10"}
        )
    data = json.loads(result)
    assert data[0]["hours"] == "4.0"


@pytest.mark.asyncio
async def test_create_time_entry() -> None:
    entry = {
        "id": 99,
        "spent_date": "2025-07-10",
        "user": {"id": 1, "name": "Jane Doe"},
        "client": {"id": 10, "name": "Acme"},
        "project": {"id": 1, "name": "Alpha"},
        "task": {"id": 1, "name": "Dev"},
        "hours": "2.5",
        "is_locked": False,
        "is_closed": False,
        "is_billed": False,
        "billable": True,
        "created_at": "2025-07-10T00:00:00Z",
        "updated_at": "2025-07-10T00:00:00Z",
    }
    with respx.mock() as mock:
        mock.route(method="POST", url__startswith=f"{HARVEST_BASE}/time_entries").mock(
            return_value=httpx.Response(200, json=entry),
        )
        result = await _call_tool(
            "create_time_entry",
            {"project_id": 1, "task_id": 1, "spent_date": "2025-07-10", "hours": 2.5},
        )
    data = json.loads(result)
    assert data["id"] == 99
    assert data["hours"] == "2.5"


@pytest.mark.asyncio
async def test_list_project_assignments() -> None:
    page = {
        "user_assignments": [
            {
                "id": 1,
                "project": {"id": 1, "name": "Alpha"},
                "user": {"id": 1, "name": "Jane Doe"},
                "is_active": True,
                "is_project_manager": False,
                "use_default_rates": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(
            method="GET",
            url__startswith=f"{HARVEST_BASE}/projects/1/user_assignments",
        ).mock(return_value=httpx.Response(200, json=page))
        result = await _call_tool("list_project_assignments", {"project_id": 1})
    data = json.loads(result)
    assert data[0]["user"]["name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_harvest_whoami() -> None:
    user = {
        "id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "timezone": "UTC",
        "is_admin": True,
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{HARVEST_BASE}/users/me").mock(
            return_value=httpx.Response(200, json=user),
        )
        result = await _call_tool("harvest_whoami")
    data = json.loads(result)
    assert data["first_name"] == "Jane"


# ---------- Forecast tools ----------


@pytest.mark.asyncio
async def test_list_forecast_projects() -> None:
    page = {
        "projects": [{"id": 1, "name": "Project X", "updated_at": "2025-01-01T00:00:00Z"}],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{FORECAST_BASE}/projects").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool("list_forecast_projects")
    data = json.loads(result)
    assert data[0]["name"] == "Project X"


@pytest.mark.asyncio
async def test_list_forecast_people() -> None:
    page = {
        "people": [
            {
                "id": 1,
                "first_name": "Jane",
                "last_name": "Doe",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{FORECAST_BASE}/people").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool("list_forecast_people")
    data = json.loads(result)
    assert data[0]["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_list_assignments() -> None:
    page = {
        "assignments": [
            {
                "id": 1,
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "updated_at": "2025-01-01T00:00:00Z",
                "project_id": 10,
                "person_id": 5,
            }
        ],
        "links": {},
    }
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{FORECAST_BASE}/assignments").mock(
            return_value=httpx.Response(200, json=page),
        )
        result = await _call_tool(
            "list_assignments", {"start_date": "2025-01-01", "end_date": "2025-01-31"}
        )
    data = json.loads(result)
    assert data[0]["id"] == 1


@pytest.mark.asyncio
async def test_create_assignment() -> None:
    assignment = {
        "id": 99,
        "start_date": "2025-02-01",
        "end_date": "2025-02-28",
        "updated_at": "2025-02-01T00:00:00Z",
        "project_id": 10,
        "person_id": 5,
    }
    with respx.mock() as mock:
        mock.route(method="POST", url__startswith=f"{FORECAST_BASE}/assignments").mock(
            return_value=httpx.Response(200, json={"assignment": assignment}),
        )
        result = await _call_tool(
            "create_assignment",
            {
                "project_id": 10,
                "person_id": 5,
                "start_date": "2025-02-01",
                "end_date": "2025-02-28",
            },
        )
    data = json.loads(result)
    assert data["id"] == 99


@pytest.mark.asyncio
async def test_update_assignment() -> None:
    assignment = {
        "id": 99,
        "start_date": "2025-03-01",
        "end_date": "2025-03-31",
        "updated_at": "2025-03-01T00:00:00Z",
        "project_id": 10,
        "person_id": 5,
    }
    with respx.mock() as mock:
        mock.route(method="PUT", url__startswith=f"{FORECAST_BASE}/assignments/99").mock(
            return_value=httpx.Response(200, json={"assignment": assignment}),
        )
        result = await _call_tool(
            "update_assignment",
            {
                "assignment_id": 99,
                "project_id": 10,
                "person_id": 5,
                "start_date": "2025-03-01",
                "end_date": "2025-03-31",
            },
        )
    data = json.loads(result)
    assert data["id"] == 99


@pytest.mark.asyncio
async def test_delete_assignment() -> None:
    with respx.mock() as mock:
        mock.route(method="DELETE", url__startswith=f"{FORECAST_BASE}/assignments/99").mock(
            return_value=httpx.Response(200),
        )
        result = await _call_tool("delete_assignment", {"assignment_id": 99})
    assert "99" in result
    assert "deleted" in result


@pytest.mark.asyncio
async def test_get_remaining_budgeted_hours() -> None:
    resp = {"remaining_budgeted_hours": [{"project_id": 1, "hours": 50.0, "budget_by": "project"}]}
    with respx.mock() as mock:
        mock.route(
            method="GET",
            url__startswith=f"{FORECAST_BASE}/aggregate/remaining_budgeted_hours",
        ).mock(return_value=httpx.Response(200, json=resp))
        result = await _call_tool("get_remaining_budgeted_hours")
    data = json.loads(result)
    assert data[0]["project_id"] == 1


@pytest.mark.asyncio
async def test_get_future_scheduled_hours() -> None:
    resp = {"future_scheduled_hours": [{"project_id": 1, "person_id": 2, "allocation": 8.0}]}
    with respx.mock() as mock:
        mock.route(
            method="GET",
            url__startswith=f"{FORECAST_BASE}/aggregate/future_scheduled_hours/2025-07-01",
        ).mock(return_value=httpx.Response(200, json=resp))
        result = await _call_tool("get_future_scheduled_hours", {"from_date": "2025-07-01"})
    data = json.loads(result)
    assert data[0]["allocation"] == 8.0


@pytest.mark.asyncio
async def test_get_project_heatmap() -> None:
    resp = [{"start_date": "2025-07-01", "end_date": "2025-07-01"}]
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{FORECAST_BASE}/aggregate/heatmap/project").mock(
            return_value=httpx.Response(200, json=resp)
        )
        result = await _call_tool(
            "get_project_heatmap",
            {"project_id": 1, "from_date": "2025-07-01", "to_date": "2025-07-31"},
        )
    data = json.loads(result)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_person_heatmap() -> None:
    resp = [
        {
            "start_date": "2025-07-01",
            "end_date": "2025-07-01",
            "daily_allocation": 480,
            "daily_time_off": 0,
        }
    ]
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{FORECAST_BASE}/aggregate/heatmap/person").mock(
            return_value=httpx.Response(200, json=resp)
        )
        result = await _call_tool(
            "get_person_heatmap",
            {"person_id": 5, "from_date": "2025-07-01", "to_date": "2025-07-31"},
        )
    data = json.loads(result)
    assert data[0]["daily_allocation"] == 480


@pytest.mark.asyncio
async def test_forecast_whoami() -> None:
    resp = {"current_user": {"id": 1, "account_ids": [123, 456]}}
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{FORECAST_BASE}/whoami").mock(
            return_value=httpx.Response(200, json=resp),
        )
        result = await _call_tool("forecast_whoami")
    data = json.loads(result)
    assert data["id"] == 1


# ---------- error handling ----------


@pytest.mark.asyncio
async def test_harvest_error_handling() -> None:
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{HARVEST_BASE}/projects").mock(
            return_value=httpx.Response(403, json={"error": "Forbidden"}),
        )
        result = await _call_tool("list_harvest_projects")
    assert "403" in result


@pytest.mark.asyncio
async def test_forecast_error_handling() -> None:
    with respx.mock() as mock:
        mock.route(method="GET", url__startswith=f"{FORECAST_BASE}/projects").mock(
            return_value=httpx.Response(404, json={"errors": ["not found"]}),
        )
        result = await _call_tool("list_forecast_projects")
    assert "404" in result


@pytest.mark.asyncio
async def test_missing_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    from mcp.server.fastmcp.exceptions import ToolError

    for key in (
        "HARVEST_ACCESS_TOKEN",
        "HARVEST_ACCOUNT_ID",
        "FORECAST_ACCESS_TOKEN",
        "FORECAST_ACCOUNT_ID",
        "HARVEST_USER_AGENT",
    ):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ToolError, match="Missing required environment variables"):
        await _call_tool("list_harvest_projects")
