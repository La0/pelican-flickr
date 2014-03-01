import tempfile
import os
import flickrapi
import logging
import main
from pelican.utils import slugify
import json

logger = logging.getLogger(__name__)

class FlickrCache:
  cache_dir = None
  api = None

  # Flickr data
  sets = []
  photos = []

  def __init__(self):

    # Setup cache dir
    if not self.cache_dir:
      self.cache_dir = os.path.join(tempfile.gettempdir(), 'pelican_flickr')
    if main.FLICKR_CACHE and not os.path.isdir(self.cache_dir):
      os.mkdir(self.cache_dir)

    # Init flickr api
    self.api = flickrapi.FlickrAPI(main.FLICKR_API_KEY)

  def build(self):
    '''
    Build cache using data from flickr api
    '''

    # Get photosets
    sets = self.api.photosets_getList(user_id=main.FLICKR_USER)
    for photoset in sets.find('photosets').findall('photoset'):
      # TODO: handle includes / excludes
      data = photoset.attrib

      # Check cache
      cache = self.fetch(data['id'])
      if cache and cache['date_update'] == data['date_update']:
        data = cache
        logger.info("Cached Flickr photoset '%s'" % data['title'])

      else:
        # Update from api data
        data['title'] = photoset.find('title').text
        data['description'] = photoset.find('title').text
        logger.info("Update Flickr photoset '%s'" % data['title'])

        # Fetch new photos, identifying the primary photo
        data.update(self.build_photos(data['id'], data['primary']))

        self.save(data['id'], data)

      data.update(self.build_paths(data['title']))
      self.sets.append(data)

  def build_photos(self, set_id, primary_id):
    '''
    Load all photos from a given photoset
    '''
    primary = None
    photoset = []
    photos = self.api.photosets_getPhotos(photoset_id=set_id, media='photos')
    for xml in photos.find('photoset').findall('photo'):
      data = xml.attrib

      # Fetch sizes, indexed per name
      sizes = self.api.photos_getSizes(photo_id=data['id'])
      data['sizes'] = {}
      for xml in sizes.find('sizes').findall('size'):
        size = xml.attrib
        slug = slugify(size['label'], ((' ', ''),))
        data['sizes'][slug] = size

      # Save
      self.save(data['id'], data)
      self.photos.append(data)
      photoset.append(data)

      # Check primary
      if data['id'] == primary_id:
        primary = data

    return {
      'photos' : photoset,
      'primary' : primary,
    }

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

  def export(self):
    '''
    Export cache in templates context
    '''
    return {
      'flickr_sets' : self.sets,
    }

  def fetch(self, name):
    '''
    Get a data set from cache
    '''
    if not main.FLICKR_CACHE:
      return False

    path = self.get_cache_path(name)
    if not os.path.exists(path):
      return False
    with open(path, 'r') as f:
      return json.loads(f.read())

  def save(self, name, data):
    '''
    Save a serializable data set in local cache
    '''
    if not main.FLICKR_CACHE:
      return False

    with open(self.get_cache_path(name), 'w') as f:
      f.write(json.dumps(data))
    return True

  def get_cache_path(self, name):
    return os.path.join(self.cache_dir, '%s.json' % name)
