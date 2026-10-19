import pytest
from pydantic import ValidationError

from taskboard.validation import TaskIn, TaskQuery

pytestmark = pytest.mark.unit


def test_defaults():
    task = TaskIn(title="Write notes")
    assert (task.done, task.priority, task.board_id) == (False, "normal", None)


def test_title_is_trimmed():
    assert TaskIn(title="  Write notes  ").title == "Write notes"


@pytest.mark.parametrize("body, bad_field", [
    ({}, "title"),
    ({"title": ""}, "title"),
    ({"title": "   "}, "title"),                 # only spaces: empty once trimmed
    ({"title": "x" * 201}, "title"),
    ({"title": "x", "priority": "urgent"}, "priority"),
    ({"title": "x", "done": "maybe"}, "done"),
    ({"title": "x", "colour": "red"}, "colour"),  # unknown fields are refused
])
def test_bad_task_bodies(body, bad_field):
    with pytest.raises(ValidationError) as e:
        TaskIn.model_validate(body)
    assert bad_field in [err["loc"][0] for err in e.value.errors()]


@pytest.mark.parametrize("args, ok", [
    ({"page": "1", "per_page": "100"}, True),
    ({"per_page": "101"}, False),
    ({"page": "0"}, False),
    ({"sort": "-title"}, True),
    ({"sort": "colour"}, False),
    ({"done": "true"}, True),
])
def test_query_limits(args, ok):
    try:
        TaskQuery.model_validate(args)
        assert ok
    except ValidationError:
        assert not ok
