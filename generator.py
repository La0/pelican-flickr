from pelican import generators
import re
import unicodedata
import main

class FlickrGenerator(generators.Generator):
  template_source = 'flickr_set.html'

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
