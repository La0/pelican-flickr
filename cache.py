import tempfile
import os
import flickrapi
import logging
import main
from pelican.utils import slugify

logger = logging.getLogger(__name__)

class FlickrCache:
  cache_dir = None

  # Flickr data
  sets = []

  def __init__(self):

    # Setup cache dir
    if not self.cache_dir:
      self.cache_dir = os.path.join(tempfile.gettempdir(), 'pelican_flickr')
    if not os.path.isdir(self.cache_dir):
      os.mkdir(self.cache_dir)

  def build(self):
    '''
    Build cache using data from flickr api
    '''
    # Init flickr api
    flickr = flickrapi.FlickrAPI(main.FLICKR_API_KEY)

    # Get photosets
    sets = flickr.photosets_getList(user_id=main.FLICKR_USER)
    for photoset in sets.find('photosets').findall('photoset'):
      # TODO: handle includes / excludes
      s = photoset.attrib
      s['title'] = photoset.find('title').text
      s['description'] = photoset.find('title').text
      s.update(self.build_paths(s['title']))
      logger.debug("Found Flickr photoset '%s'" % s['title'])
      self.sets.append(s)

  def build_paths(self, title):
    '''
    Build path, url, and slug for a cache object
    '''
    slug = slugify(title)
    path = '%s/%s.html' % (main.FLICKR_OUTPUT_DIRNAME, slug)
    return {
      'slug' : slug,
      'path' : path,
      'url' : '/' + path,
    }


