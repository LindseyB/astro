"""
Last.fm API service for fetching top tracks by genre
"""
import os
import random
from collections.abc import Sequence
from datetime import datetime
from typing import TypedDict

import requests
from config import logger

# Last.fm API configuration
LASTFM_API_KEY = os.environ.get("LAST_FM_API_KEY")
LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"
TOP_TIER_RATIO = 0.33
MID_TIER_RATIO = 0.66
TOP_TARGET_RATIO = 0.40
MID_TARGET_RATIO = 0.35


class TrackInfo(TypedDict):
    name: str
    artist: str


def select_varied_tracks(tracks: Sequence[TrackInfo], limit: int = 30, seed_key: str | None = None) -> list[TrackInfo]:
    """
    Select a varied mix of tracks from popularity tiers while staying in-genre.

    Strategy:
      - 40% from top tier
      - 35% from middle tier
      - 25% from tail tier
    Selection is deterministic per day/genre when seed_key is provided.
    """
    if not tracks:
        return []

    if limit <= 0:
        return []

    if len(tracks) <= limit:
        return list(tracks)

    top_end = max(1, int(len(tracks) * TOP_TIER_RATIO))
    mid_end = max(top_end + 1, int(len(tracks) * MID_TIER_RATIO))

    top_tier = tracks[:top_end]
    mid_tier = tracks[top_end:mid_end]
    tail_tier = tracks[mid_end:]

    top_target = max(1, int(round(limit * TOP_TARGET_RATIO)))
    mid_target = max(1, int(round(limit * MID_TARGET_RATIO)))
    tail_target = max(0, limit - top_target - mid_target)

    if seed_key is None:
        seed_key = datetime.utcnow().strftime('%Y-%m-%d')

    rng = random.Random(str(seed_key))

    def sample_tier(tier: Sequence[TrackInfo], count: int) -> list[TrackInfo]:
        if count <= 0 or not tier:
            return []
        if len(tier) <= count:
            picked = list(tier)
            rng.shuffle(picked)
            return picked
        return rng.sample(tier, count)

    selected = []
    selected.extend(sample_tier(top_tier, top_target))
    selected.extend(sample_tier(mid_tier, mid_target))
    selected.extend(sample_tier(tail_tier, tail_target))

    if len(selected) < limit:
        remaining = [track for track in tracks if track not in selected]
        if remaining:
            rng.shuffle(remaining)
            selected.extend(remaining[: limit - len(selected)])

    rng.shuffle(selected)
    return selected[:limit]


def get_top_tracks_by_genre(genre: str, limit: int = 30) -> list[TrackInfo]:
    """
    Fetch top tracks for a given genre from Last.fm API
    
    Args:
        genre (str): Music genre tag to search for
        limit (int): Number of tracks to return (default 30, max 50)
    
    Returns:
        list: List of track dictionaries with 'name' and 'artist' keys
              Returns empty list if API call fails or no API key configured
    """
    if not LASTFM_API_KEY:
        logger.warning("LAST_FM_API_KEY environment variable is not set")
        return []
    
    # Skip if genre is "any" or empty
    if not genre or genre.lower() == "any":
        logger.debug("Genre is 'any' or empty, skipping Last.fm API call")
        return []
    
    # Sanitize genre for API call
    genre_tag = genre.strip().lower()
    
    try:
        logger.info(f"Fetching top tracks for genre: {genre_tag}")
        
        params = {
            'method': 'tag.gettoptracks',
            'tag': genre_tag,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'limit': min(limit, 50)  # Last.fm API has a max limit
        }
        
        response = requests.get(LASTFM_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse tracks from response
        if 'tracks' not in data or 'track' not in data['tracks']:
            logger.warning(f"No tracks found for genre: {genre_tag}")
            return []
        
        tracks: list[TrackInfo] = []
        for track in data['tracks']['track']:
            track_name = str(track.get('name', '') or '')
            artist_value = track.get('artist', {})
            if isinstance(artist_value, dict):
                artist_name = str(artist_value.get('name', '') or '')
            else:
                artist_name = str(artist_value or '')
            
            # Only add tracks with both name and artist
            if track_name and artist_name:
                tracks.append({'name': track_name, 'artist': artist_name})
        
        logger.info(f"Found {len(tracks)} tracks for genre: {genre_tag}")
        return tracks
        
    except requests.exceptions.Timeout:
        logger.error(f"Last.fm API timeout for genre: {genre_tag}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Last.fm API request failed for genre {genre_tag}: {e}")
        return []
    except (KeyError, ValueError) as e:
        logger.error(f"Failed to parse Last.fm API response for genre {genre_tag}: {e}")
        return []


def format_tracks_for_prompt(tracks: Sequence[TrackInfo], limit: int = 30) -> str:
    """
    Format track list for inclusion in AI prompt
    
    Args:
        tracks (list): List of track dictionaries from get_top_tracks_by_genre
        limit (int): Maximum number of tracks to include (default 30)
    
    Returns:
        str: Formatted string of tracks for prompt, or empty string if no tracks
    """
    if not tracks:
        return ""
    
    # Use a deterministic daily seed so suggestions rotate over time but are stable within a day.
    daily_seed = datetime.utcnow().strftime('%Y-%m-%d')
    limited_tracks = select_varied_tracks(tracks, limit=limit, seed_key=daily_seed)
    
    # Format as bullet list
    track_lines = [f"- {track['name']} by {track['artist']}" for track in limited_tracks]
    
    return "Popular tracks in this genre include:\n" + "\n".join(track_lines)
