from pelican import generators
import re
import unicodedata
import main
import os

class FlickrGenerator(generators.Generator):
  template_set = 'flickr_set.html'
  template_photo = 'flickr_photo.html'

  def __init__(self, context, settings, path, theme, output_path, **kwargs):

    # Add our templates dir to _templates_path
    paths = settings.get('EXTRA_TEMPLATES_PATHS', [])
    paths.append(os.path.join(os.path.dirname(__file__), 'templates'))
    settings['EXTRA_TEMPLATES_PATHS'] = paths

    super(FlickrGenerator, self).__init__(context, settings, path, theme, output_path, **kwargs)

  def generate_output(self, writer):
    self.generate_photosets(writer, False) # Public photos
    self.generate_photosets(writer, True) # Private photos

  def generate_photosets(self, writer, private=False):
    '''
    Generate photosets & photos
    '''
    for photoset in main.FLICKR_CACHE.sets:
      photoset.set_privacy(private)
      self.generate_photoset(writer, photoset)
      photos = photoset.get_visible_photos()
      for i,photo in enumerate(photos):
        previous = i-1 >= 0 and photos[i-1] or None
        next = i+1 < len(photos) and photos[i+1] or None
        self.generate_photo(writer, photo, next, previous)

  def generate_photoset(self, writer, photoset):
    '''
    Generate Flickr photoset page
    '''
    self.context['photoset'] = photoset
    template = self.env.get_template(self.template_set)
    rurls = self.settings['RELATIVE_URLS']
    writer.write_file(photoset.generated_path, template, self.context, rurls, override_output=True)

  def generate_photo(self, writer, photo, next=None, previous=None):
    '''
    Generate Flickr photo page
    '''
    if not photo.is_visible():
      return

    self.context['photo'] = photo
    self.context['photo_next'] = next
    self.context['photo_previous'] = previous
    template = self.env.get_template(self.template_photo)
    rurls = self.settings['RELATIVE_URLS']
    writer.write_file(photo.generated_path, template, self.context, rurls, override_output=True)
    del self.context['photo']

