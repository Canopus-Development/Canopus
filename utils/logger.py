import logging
import os
from datetime import datetime
<<<<<<< HEAD
import warnings

class ALSAFilter(logging.Filter):
    def filter(self, record):
        return not any(x in str(record.msg) for x in [
            'ALSA lib',
            'snd_pcm',
            'Cannot open',
            'Invalid card'
        ])

def setup_logger():
=======

def setup_logger():
    logger = logging.getLogger('canopus')
    logger.setLevel(logging.INFO)

>>>>>>> origin/main
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

<<<<<<< HEAD
    # Set up main logger
    logger = logging.getLogger('canopus')
    logger.setLevel(logging.INFO)

    # File handler for main logs
    fh = logging.FileHandler(f'logs/canopus_{datetime.now().strftime("%Y%m%d")}.log')
    fh.setLevel(logging.INFO)

    # File handler for junk logs
    junk_handler = logging.FileHandler('logs/junk.log')
    junk_handler.setLevel(logging.DEBUG)

=======
    # File handler
    fh = logging.FileHandler(f'logs/canopus_{datetime.now().strftime("%Y%m%d")}.log')
    fh.setLevel(logging.INFO)

>>>>>>> origin/main
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
<<<<<<< HEAD
    junk_handler.setFormatter(formatter)

    # Set up filters
    class JunkFilter(logging.Filter):
        def filter(self, record):
            return any(x in record.msg for x in [
                'ALSA lib',
                'FutureWarning',
                'torch.load',
                'weights_only=False'
            ])

    class MainFilter(logging.Filter):
        def filter(self, record):
            return not any(x in record.msg for x in [
                'ALSA lib',
                'FutureWarning',
                'torch.load',
                'weights_only=False'
            ])

    # Apply filters
    fh.addFilter(MainFilter())
    ch.addFilter(MainFilter())
    junk_handler.addFilter(JunkFilter())
    ch.addFilter(ALSAFilter())

    # Create separate handler for ALSA messages
    alsa_handler = logging.FileHandler('logs/alsa.log')
    alsa_handler.setLevel(logging.WARNING)
    alsa_handler.setFormatter(formatter)
    
    logger.addHandler(alsa_handler)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.addHandler(junk_handler)

    # Redirect warnings to logging
    logging.captureWarnings(True)
    warnings.filterwarnings('always', category=FutureWarning)
=======

    logger.addHandler(fh)
    logger.addHandler(ch)
>>>>>>> origin/main

    return logger
