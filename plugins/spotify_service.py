import threading
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config.config import SpotifyConfig, logger

class SpotifyService:
    def __init__(self):
        self.sp = None
        self.authenticate_spotify()

    def authenticate_spotify(self):
        logger.info("Authenticating with Spotify.")
        scope = (
            "user-read-playback-state "
            "user-modify-playback-state "
            "user-library-read "
            "user-library-modify "
            "user-read-currently-playing "
            "app-remote-control "
            "streaming"
        )
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SpotifyConfig.CLIENT_ID,
            client_secret=SpotifyConfig.CLIENT_SECRET,
            redirect_uri=SpotifyConfig.REDIRECT_URI,
            scope=scope
        ))

    def play_music(self, track_uri=None):
        logger.info("Attempting to play music.")
        try:
            devices = self.sp.devices()
            if not devices['devices']:
                logger.warning("No Spotify devices available for playback.")
                return "No devices available to play music on."

            device_id = devices['devices'][0]['id']
            if track_uri:
                self.sp.start_playback(device_id=device_id, uris=[track_uri])
            else:
                self.sp.start_playback(device_id=device_id)
            logger.info("Music is playing on the available device.")
            return "Playing music on your Spotify device."
        except Exception as e:
            logger.error(f"Error playing music: {e}")
            return "Failed to play music."

    def pause_music(self):
        logger.info("Pausing music.")
        try:
            self.sp.pause_playback()
            return "Music paused."
        except Exception as e:
            logger.error(f"Error pausing music: {e}")
            return "Failed to pause music."

    def resume_music(self):
        logger.info("Resuming music.")
        try:
            self.sp.start_playback()
            return "Music resumed."
        except Exception as e:
            logger.error(f"Error resuming music: {e}")
            return "Failed to resume music."

    def shuffle_music(self, state=True):
        logger.info(f"Setting shuffle to {'on' if state else 'off'}.")
        try:
            self.sp.shuffle(state=state)
            return f"Shuffle {'enabled' if state else 'disabled'}."
        except Exception as e:
            logger.error(f"Error setting shuffle: {e}")
            return "Failed to set shuffle."

    def loop_music(self, state='context'):
        logger.info(f"Setting loop mode to {state}.")
        try:
            self.sp.repeat(state=state)
            return f"Loop mode set to {state}."
        except Exception as e:
            logger.error(f"Error setting loop mode: {e}")
            return "Failed to set loop mode."

    def skip_next(self):
        logger.info("Skipping to next track.")
        try:
            self.sp.next_track()
            return "Skipped to the next track."
        except Exception as e:
            logger.error(f"Error skipping to next track: {e}")
            return "Failed to skip to the next track."

    def skip_previous(self):
        logger.info("Skipping to previous track.")
        try:
            self.sp.previous_track()
            return "Skipped to the previous track."
        except Exception as e:
            logger.error(f"Error skipping to previous track: {e}")
            return "Failed to skip to the previous track."

    def execute(self, command):
        if "play music" in command:
            track_uri = None
            if "track" in command:
                track_name = command.split("track ")[-1]
                results = self.sp.search(q=track_name, limit=1, type='track')
                if results['tracks']['items']:
                    track_uri = results['tracks']['items'][0]['uri']
            return self.play_music(track_uri)

        elif "pause" in command:
            return self.pause_music()

        elif "resume" in command:
            return self.resume_music()

        elif "shuffle" in command:
            state = "on" in command
            return self.shuffle_music(state)

        elif "loop" in command:
            if "one" in command:
                return self.loop_music(state='track')
            elif "off" in command:
                return self.loop_music(state='off')
            else:
                return self.loop_music(state='context')

        elif "next" in command:
            return self.skip_next()

        elif "previous" in command:
            return self.skip_previous()

        return None


def create_spotify_service():
    spotify_service = SpotifyService()

    def start_service():
        spotify_service.authenticate_spotify()
        logger.info("Spotify service started.")

    # Run Spotify service in a separate thread
    service_thread = threading.Thread(target=start_service)
    service_thread.start()

    return spotify_service

# To be called by the AI assistant for loading the plugin
def execute(command):
    spotify_service = create_spotify_service()
    response = spotify_service.execute(command)
    return response
