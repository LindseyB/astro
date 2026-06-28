from collections.abc import Iterator
import inspect

from ai_service import call_ai_api, get_client, stream_ai_api, verify_song_exists
from ask_routes import ask_anything, stream_ask_anything
from chart_data import (
    create_charts,
    get_current_planets,
    get_full_chart_structure,
    get_main_positions,
    get_planets_in_houses,
)
from chart_routes import (
    chart,
    full_chart,
    index,
    live_mas,
    stream_chart_analysis,
    stream_full_chart_analysis,
    stream_live_mas_analysis,
)
from calculations import (
    _format_full_chart_houses,
    _format_full_chart_planets,
    _format_planets_in_houses,
    stream_calculate_ask_anything,
    stream_calculate_chart,
    stream_calculate_full_chart,
    stream_calculate_live_mas,
)
from formatters import (
    format_planets_for_api,
    format_planets_in_houses_for_prompt,
    markdown_filter,
    prepare_music_genre_text,
)
from lastfm_service import format_tracks_for_prompt, get_top_tracks_by_genre, select_varied_tracks
from launchdarkly_service import get_launchdarkly_service, should_show_chart_wheel
from music_routes import music_suggestion
from prompt_templates import load_prompt_template, load_prompt_text, render_prompt_template
from route_helpers import _require_ai_client
from routes import get_user_ip, inject_site_meta
from validation import find_missing_fields
from tests.test_config import MockEnvironment, create_test_app
from tests.test_secret_key_config import _run_import_routes_with_env


ANNOTATED_FUNCTIONS = [
    get_client,
    call_ai_api,
    stream_ai_api,
    verify_song_exists,
    stream_calculate_chart,
    stream_calculate_live_mas,
    stream_calculate_full_chart,
    stream_calculate_ask_anything,
    select_varied_tracks,
    get_top_tracks_by_genre,
    format_tracks_for_prompt,
    create_charts,
    get_main_positions,
    get_planets_in_houses,
    get_current_planets,
    get_full_chart_structure,
    markdown_filter,
    prepare_music_genre_text,
    format_planets_in_houses_for_prompt,
    format_planets_for_api,
    load_prompt_template,
    load_prompt_text,
    render_prompt_template,
    find_missing_fields,
    _require_ai_client,
    get_launchdarkly_service,
    should_show_chart_wheel,
    ask_anything,
    stream_ask_anything,
    index,
    chart,
    stream_chart_analysis,
    full_chart,
    stream_full_chart_analysis,
    live_mas,
    stream_live_mas_analysis,
    music_suggestion,
    inject_site_meta,
    get_user_ip,
]

INTERNAL_TYPED_HELPERS = [
    _format_planets_in_houses,
    _format_full_chart_planets,
    _format_full_chart_houses,
    create_test_app,
    MockEnvironment.__init__,
    MockEnvironment.__enter__,
    MockEnvironment.__exit__,
    _run_import_routes_with_env,
]


def test_public_issue_114_functions_have_parameter_and_return_annotations():
    for function in ANNOTATED_FUNCTIONS:
        signature = inspect.signature(function)

        for parameter in signature.parameters.values():
            if parameter.name in {"self", "cls"}:
                continue
            assert parameter.annotation is not inspect.Signature.empty, function.__name__

        assert signature.return_annotation is not inspect.Signature.empty, function.__name__


def test_streaming_public_functions_are_typed_as_iterators_of_strings():
    streaming_functions = [
        stream_ai_api,
        stream_calculate_chart,
        stream_calculate_live_mas,
        stream_calculate_full_chart,
        stream_calculate_ask_anything,
    ]

    for function in streaming_functions:
        assert inspect.signature(function).return_annotation == Iterator[str]


def test_remaining_internal_helpers_have_parameter_and_return_annotations():
    for function in INTERNAL_TYPED_HELPERS:
        signature = inspect.signature(function)

        for parameter in signature.parameters.values():
            if parameter.name in {"self", "cls"}:
                continue
            assert parameter.annotation is not inspect.Signature.empty, function.__qualname__

        assert signature.return_annotation is not inspect.Signature.empty, function.__qualname__