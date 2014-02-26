from pelican import signals, generators
import tempfile
import os
import re
import unicodedata
import flickrapi
import logging

logger = logging.getLogger(__name__)

FLICKR_DIR = ''
FLICKR_CACHE = {
  'sets' : [],
}

class FlickrGenerator(generators.Generator):
  template_source = 'flickr_set.html'

  def generate_output(self, writer):
    for photoset in FLICKR_CACHE['sets']:
      self.generate_photoset(writer, photoset)


  def generate_photoset(self, writer, photoset):
    '''
    Generate Flickr photoset page
    '''
    self.context['photoset'] = photoset
    slug = self.slugify(photoset['title'])
    dest = 'flickr/%s.html' % slug
    template = self.env.get_template(self.template_source)
    rurls = self.settings['RELATIVE_URLS']
    writer.write_file(dest, template, self.context, rurls, override_output=True)

  def slugify(self, s):

    # Remove all accents
    try:
      s = unicode(s, 'ISO-8859-1')
    except:
      pass
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')

    # Remove all non allowed chars
    s = re.sub('[^a-z0-9 ]', '', s.strip().lower(),)

    # Remove multiple spaces
    s = re.sub('[ ]+', ' ', s.strip().lower(),)

    # Replace space by -
    s = s.replace(' ', '-')
    return s

def register():
  signals.initialized.connect(init_flickr)
  signals.get_generators.connect(add_generator)

def add_generator(generators):
  return FlickrGenerator


def build_cache():
  '''
  Build local flickr cache
  '''
  global FLICKR_CACHE
  flickr = flickrapi.FlickrAPI(FLICKR_API_KEY)

  # Get photosets
  sets = flickr.photosets_getList(user_id=FLICKR_USER)
  for photoset in sets.find('photosets').findall('photoset'):
    # TODO: handle includes / excludes
    s = photoset.attrib
    s['title'] = photoset.find('title').text
    s['description'] = photoset.find('title').text
    FLICKR_CACHE['sets'].append(s)


def init_flickr(sender):
  global FLICKR_DIR

  # Load mandatory settings
  settings = {
    'FLICKR_API_KEY' : True,
    'FLICKR_USER' : True,
    'FLICKR_DIR' : False,
  }
  for setting, mandatory in settings.items():
    val = sender.settings.get(setting, None)
    if mandatory and not val:
      raise Exception('Missing %s settings' % setting)
    globals()[setting] = val
    logger.debug('Read setting %s = %s' % (setting, val))
  '''
  # Work dir
  if not FLICKR_DIR:
    FLICKR_DIR = os.path.join(tempfile.gettempdir(), 'pelican_flickr')
  if not os.path.isdir(FLICKR_DIR):
    os.mkdir(FLICKR_DIR)
  '''
  build_cache()
