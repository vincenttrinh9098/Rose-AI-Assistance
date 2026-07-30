"""
run_tests.py

Runs a battery of functional tests against Rose's core systems.
Not a full pytest suite - a lightweight sanity-check runner for
catching regressions after changes.
"""

import sys


def run_all_tests(progress_callback=None):
    """
    Runs all tests, returns (passed_count, failed_count, failures_list).
    progress_callback(name, success, error), if provided, is called after each test.
    """
    passed = 0
    failed = 0
    failures = []

    def test(name):
        def decorator(func):
            nonlocal passed, failed
            try:
                func()
                passed += 1
                if progress_callback:
                    progress_callback(name, True, None)
            except Exception as e:
                failed += 1
                failures.append((name, str(e)))
                if progress_callback:
                    progress_callback(name, False, str(e))
            return func
        return decorator

    def assert_true(condition, message="Assertion failed"):
        if not condition:
            raise AssertionError(message)

    # --- Core routing tests ---

    @test("get_action() handles empty input")
    def _():
        from ai.llm import get_action
        result = get_action("")
        assert_true(result.get("action") in ("none", "offline"), f"Expected none/offline, got {result}")


    @test("get_action() routes 'open spotify' correctly")
    def _():
        from ai.llm import get_action
        result = get_action("open spotify")
        assert_true(result.get("action") == "open_app", f"Expected open_app, got {result}")


    @test("get_action() routes calendar edit correctly")
    def _():
        from ai.llm import get_action
        result = get_action("change my 3pm meeting to 5pm")
        assert_true(result.get("action") == "edit_calendar_event", f"Expected edit_calendar_event, got {result}")


    # --- Event parsing tests ---

    @test("extract_date() handles empty input")
    def _():
        from ai.event_parser import extract_date
        result = extract_date("")
        assert_true(result, "extract_date returned empty result for empty input")


    @test("extract_event() handles empty input")
    def _():
        from ai.event_parser import extract_event
        result = extract_event("")
        assert_true(result.get("has_details") == False, f"Expected has_details=False, got {result}")


    # --- Dispatch smoke tests (things that shouldn't crash) ---

    @test("dispatch() handles empty input without crashing")
    def _():
        from core.dispatcher import dispatch
        result = dispatch("")
        assert_true(isinstance(result, str), "dispatch() should always return a string")


    @test("dispatch() handles gibberish without crashing")
    def _():
        from core.dispatcher import dispatch
        result = dispatch("asdkfj alskdjf laksjdf")
        assert_true(isinstance(result, str), "dispatch() should always return a string")


    # --- Memory tests ---

    @test("long-term memory round-trips correctly")
    def _():
        from core.long_term_memory import remember_fact, load_memory
        remember_fact("preferences", "_test_key", "_test_value")
        memory = load_memory()
        assert_true(memory["preferences"].get("_test_key") == "_test_value", "Fact wasn't stored correctly")
        # cleanup
        del memory["preferences"]["_test_key"]
        from core.long_term_memory import save_memory
        save_memory(memory)


    @test("conversation history never stores empty exchanges")
    def _():
        from core.conversation import add_exchange, get_history, clear
        clear()
        add_exchange("", "some response")
        history = get_history()
        assert_true(len(history) == 0, f"Expected empty history after adding blank exchange, got {history}")


    # --- Config file tests ---

    @test("apps.json loads without crashing")
    def _():
        from commands.applications import _apps
        assert_true(isinstance(_apps, dict), "_apps should be a dict")


    @test("open_app() handles empty input")
    def _():
        from commands.applications import open_app
        result = open_app("")
        assert_true(isinstance(result, str), "open_app() should always return a string")










    # --- Calendar: creation ---

    @test("add_google_calendar_event() creates and returns an ID")
    def _():
        from commands.google_calendar import add_google_calendar_event
        message, event_id = add_google_calendar_event("_TestEvent", "August 15, 2026", "10:00 AM", 1)
        assert_true(event_id is not None, f"Expected a real event ID, got None. Message: {message}")


    @test("find_google_events_for_edit() finds events by exact date")
    def _():
        from commands.google_calendar import find_google_events_for_edit
        events = find_google_events_for_edit("August 15, 2026", "_TestEvent")
        assert_true(len(events) >= 1, f"Expected to find _TestEvent, got {events}")


    import time as time_module

    @test("find_google_events_for_edit() respects timezone day boundaries")
    def _():
        from commands.google_calendar import add_google_calendar_event, find_google_events_for_edit
        import time as time_module
        unique_name = f"_TZTest{int(time_module.time())}"
        add_google_calendar_event(unique_name, "August 20, 2026", "9:00 PM", 1)
        time_module.sleep(1)
        same_day = find_google_events_for_edit("August 20, 2026", unique_name)
        next_day = find_google_events_for_edit("August 21, 2026", unique_name)
        assert_true(len(same_day) >= 1, f"Expected at least one event on correct day, found {same_day}")
        assert_true(len(next_day) == 0, f"Event incorrectly leaked to next day: {next_day}")

    # --- Calendar: editing ---

    @test("edit_google_calendar_event() preserves date when only changing time")
    def _():
        from commands.google_calendar import find_google_events_for_edit, edit_google_calendar_event
        events = find_google_events_for_edit("August 15, 2026", "_TestEvent")
        assert_true(len(events) >= 1, "Setup failed - no _TestEvent found")
        event_id = events[0]["id"]
        edit_google_calendar_event(event_id, new_time="11:00 AM")
        updated = find_google_events_for_edit("August 15, 2026", "_TestEvent")
        assert_true(len(updated) >= 1, "Event should still be on August 15 after time-only edit")


    @test("extract_edit() detects placeholder title_hint correctly")
    def _():
        from ai.event_parser import extract_edit
        result = extract_edit("actually make that 3pm")
        title_hint = result.get("title_hint", "")
        is_placeholder = not title_hint or "UNKNOWN" in title_hint.upper()
        assert_true(is_placeholder, f"Expected placeholder-like title_hint for bare correction, got '{title_hint}'")


    # --- Calendar: last-event reference ---

    @test("last_calendar_event tracks correctly after creation")
    def _():
        from core.dispatcher import dispatch
        from core.last_calendar_event import get_last_event
        dispatch("set a google event for _TestLastEvent at 4pm today")
        last = get_last_event()
        assert_true(last is not None and "TestLastEvent" in last.get("summary", ""), f"Expected TestLastEvent tracked, got {last}")


    @test("'actually make that X' resolves via last_event, not a fresh search")
    def _():
        from core.dispatcher import dispatch
        from commands.google_calendar import find_google_events_for_edit
        dispatch("set a google event for _TestRefEvent at 2pm today")
        response = dispatch("actually make that 3pm")
        assert_true("couldn't find" not in response.lower(), f"Expected reference to resolve, got: {response}")


    # --- Disambiguation ---

    @test("disambiguation triggers with multiple similarly-named events")
    def _():
        from core.dispatcher import dispatch
        dispatch("set a google event for Zebra Meeting Alpha at 1pm today")
        dispatch("set a google event for Zebra Meeting Beta at 2pm today")
        response = dispatch("change my zebra meeting to 5pm")
        assert_true("which one" in response.lower() or "found a few" in response.lower(), f"Expected disambiguation prompt, got: {response}")


    @test("cancel during disambiguation clears pending state")
    def _():
        from core.dispatcher import dispatch
        from core.pending_action import get_pending
        dispatch("set a google event for _TestCancel one at 1pm today")
        dispatch("set a google event for _TestCancel two at 2pm today")
        dispatch("change my _TestCancel event to 5pm")
        dispatch("cancel")
        assert_true(get_pending() is None, "Pending state should be cleared after cancel")


    # --- Messages / contacts ---

    @test("find_contact_matches() returns a list, not crashes, for nonexistent name")
    def _():
        from commands.messages import find_contact_matches
        result = find_contact_matches("ZZZNonexistentPersonZZZ")
        assert_true(isinstance(result, list), "Should return an empty list, not crash")
        assert_true(len(result) == 0, f"Expected no matches, got {result}")


    # --- File search ---

    @test("search_files() handles very short/garbage queries safely")
    def _():
        from commands.files import search_files
        result = search_files("a")
        assert_true(isinstance(result, list), "search_files should always return a list")


    # --- Config-driven commands ---

    @test("open_app() falls back gracefully for unknown app")
    def _():
        from commands.applications import open_app
        result = open_app("ZZZDefinitelyNotARealAppZZZ")
        assert_true(isinstance(result, str), "Should return a string, not crash")


    @test("search_site() handles unknown site")
    def _():
        from commands.browser import search_site
        result = search_site("not_a_real_site", "test")
        assert_true("don't know" in result.lower(), f"Expected graceful failure, got: {result}")


    # --- Plugin registry integrity ---

    @test("every registered plugin has required attributes")
    def _():
        from plugins.registry import ALL_PLUGINS
        for p in ALL_PLUGINS:
            assert_true(hasattr(p, "name") and p.name, f"Plugin {p} missing a name")
            assert_true(hasattr(p, "description") and p.description, f"Plugin {p.name} missing a description")
            assert_true(hasattr(p, "handle"), f"Plugin {p.name} missing handle()")


    @test("no duplicate plugin names in registry")
    def _():
        from plugins.registry import ALL_PLUGINS
        names = [p.name for p in ALL_PLUGINS]
        assert_true(len(names) == len(set(names)), f"Duplicate plugin names found: {names}")


    # --- Cleanup ---

    @test("cleanup test calendar events")
    def _():
        from commands.google_calendar import find_google_events_for_edit, delete_google_calendar_event
        for term in ["_Test", "_TestEvent", "_TestDup", "_TestCancel", "_TestRefEvent", "_TestLastEvent", "_TestEveningEvent"]:
            for date in ["August 15, 2026", "July 30, 2026"]:
                for e in find_google_events_for_edit(date, term):
                    delete_google_calendar_event(e["id"])

    return passed, failed, failures

def test(name):
    """Decorator-style helper: wraps a test function with pass/fail tracking."""
    def decorator(func):
        global passed, failed
        try:
            func()
            passed += 1
            print(f"✓ {name}")
        except Exception as e:
            failed += 1
            failures.append((name, str(e)))
            print(f"✗ {name} - {e}")
        return func
    return decorator









if __name__ == "__main__":
    import sys
    passed, failed, failures = run_all_tests(progress_callback=lambda name, ok, err: print(f"{'✓' if ok else '✗'} {name}" + (f" - {err}" if err else "")))
    print(f"\nPassed: {passed}  Failed: {failed}")
    sys.exit(1 if failed > 0 else 0)