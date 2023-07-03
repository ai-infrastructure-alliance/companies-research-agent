from urllib.parse import urlparse, urlunparse
from requests_html import HTMLSession


def remove_www(url):
  parsed_url = urlparse(url)
  netloc = parsed_url.netloc.replace("www.", "")
  return urlunparse((parsed_url.scheme, netloc, parsed_url.path,
                     parsed_url.params, parsed_url.query, parsed_url.fragment))


def get_final_url(url):
  session = HTMLSession()
  try:
    response = session.get(url)
    response.html.render(timeout=60.0)
    return response.url
  except Exception as e:
    print(f"Error: {e}")
    return None


def clean_url(url):
  try:
    print(f"Cleaning {url}")
    url = get_final_url(url)
    if not url:
      return None
    parsed_url = urlparse(url)
    cleaned_url = parsed_url._replace(query="")
    if not cleaned_url.scheme:
      cleaned_url = cleaned_url._replace(scheme='https')
    new_url = urlunparse(cleaned_url)
    new_url = new_url.replace('///', '//')
    new_url = remove_www(new_url)
    if new_url.endswith('/'):
      new_url = new_url[:-1]
    print(f"Cleaned to {new_url}")
    return new_url
  except Exception as e:
    print(f"Error: {e}")
    return None
