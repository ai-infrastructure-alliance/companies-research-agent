from urllib.parse import urlparse, urlunparse


def remove_www(url):
  parsed_url = urlparse(url)
  netloc = parsed_url.netloc.replace("www.", "")
  return urlunparse((parsed_url.scheme, netloc, parsed_url.path,
                     parsed_url.params, parsed_url.query, parsed_url.fragment))


def clean_url(url):
  parsed_url = urlparse(url)
  cleaned_url = parsed_url._replace(query="")
  if not cleaned_url.scheme:
    cleaned_url = cleaned_url._replace(scheme='https')
  new_url = urlunparse(cleaned_url)
  new_url = new_url.replace('///', '//')
  new_url = remove_www(new_url)
  if new_url.endswith('/'):
    new_url = new_url[:-1]
  return new_url