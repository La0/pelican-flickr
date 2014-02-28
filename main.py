from pelican import signals
import tempfile
import os
import flickrapi
import logging
from .generator import FlickrGenerator
from .cache import FlickrCache

logger = logging.getLogger(__name__)

def register():
  signals.initialized.connect(init_flickr)
  signals.get_generators.connect(add_generator)

def add_generator(generators):
  return FlickrGenerator

def init_flickr(sender):

  # Load mandatory settings
  settings = {
    'FLICKR_API_KEY' : {
      'mandatory' : True,
    },
    'FLICKR_USER' : {
      'mandatory' : True,
    },
    'FLICKR_OUTPUT_DIRNAME' : {
      'mandatory' : False,
      'default' : 'flickr',
    }
  }
  for setting, conf in settings.items():
    val = sender.settings.get(setting, None)
    if conf['mandatory'] and not val:
      raise Exception('Missing %s settings' % setting)
    globals()[setting] = val or conf['default']
    logger.debug('Read setting %s = %s' % (setting, val))

  # Init cache
  cache = FlickrCache()
  cache.build()
  globals()['FLICKR_CACHE'] = cache
