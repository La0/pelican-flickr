from pelican import generators
import re
import unicodedata
import main
import os

class FlickrGenerator(generators.Generator):
  template_source = 'flickr_set.html'

  def __init__(self, context, settings, path, theme, output_path, **kwargs):

    # Add our templates dir to _templates_path
    paths = settings.get('EXTRA_TEMPLATES_PATHS', [])
    paths.append(os.path.join(os.path.dirname(__file__), 'templates'))
    settings['EXTRA_TEMPLATES_PATHS'] = paths

    super(FlickrGenerator, self).__init__(context, settings, path, theme, output_path, **kwargs)

  def generate_output(self, writer):

    for photoset in main.FLICKR_CACHE.sets:
      self.generate_photoset(writer, photoset)


  def generate_photoset(self, writer, photoset):
    '''
    Generate Flickr photoset page
    '''
    self.context['photoset'] = photoset
    template = self.env.get_template(self.template_source)
    rurls = self.settings['RELATIVE_URLS']
    writer.write_file(photoset['path'], template, self.context, rurls, override_output=True)
