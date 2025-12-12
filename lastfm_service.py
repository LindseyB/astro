"""
Last.fm API service for fetching top tracks by genre
"""
import os
import requests
from config import logger

# Last.fm API configuration
LASTFM_API_KEY = os.environ.get("LAST_FM_API_KEY")
LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"


def get_top_tracks_by_genre(genre, limit=20):
    """
    Fetch top tracks for a given genre from Last.fm API
    
    Args:
        genre (str): Music genre tag to search for
        limit (int): Number of tracks to return (default 20, max 50)
    
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
        
        tracks = []
        for track in data['tracks']['track']:
            track_info = {
                'name': track.get('name', ''),
                'artist': track.get('artist', {}).get('name', '') if isinstance(track.get('artist'), dict) else track.get('artist', '')
            }
            
            # Only add tracks with both name and artist
            if track_info['name'] and track_info['artist']:
                tracks.append(track_info)
        
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


def format_tracks_for_prompt(tracks, limit=20):
    """
    Format track list for inclusion in AI prompt
    
    Args:
        tracks (list): List of track dictionaries from get_top_tracks_by_genre
        limit (int): Maximum number of tracks to include (default 20)
    
    Returns:
        str: Formatted string of tracks for prompt, or empty string if no tracks
    """
    if not tracks:
        return ""
    
    # Take only the specified limit
    limited_tracks = tracks[:limit]
    
    # Format as bullet list
    track_lines = [f"- {track['name']} by {track['artist']}" for track in limited_tracks]
    
    return "Popular tracks in this genre include:\n" + "\n".join(track_lines)
