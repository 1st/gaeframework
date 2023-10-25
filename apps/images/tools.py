'''
Images tools.
'''
from google.appengine.api import images, blobstore, files
from google.appengine.api.images import get_serving_url

#def upload_image(file_data):
    
def prepare_image(data):
  try:
    if len(data) > 1024 * 1024: raise PhotoRpcError(PhotoRpcError.RPC_LONG_DATA)
    image = images.Image(data)
    width, height = get_config('experika.company', 'logo_size')
    image.resize(width, height)
    image.execute_transforms(images.JPEG, 85)
  except (images.NotImageError, images.BadImageError):
    raise PhotoRpcError(PhotoRpcError.RPC_WRONG_TYPE)
  except (images.LargeImageError, apiproxy_errors.RequestTooLargeError):
    raise PhotoRpcError(PhotoRpcError.RPC_LONG_DATA)
  return image._image_data


def save_image(data, user_id, typ):
  file_name = files.blobstore.create('image/jpeg', '%s_%s.jpeg' % (user_id, typ))
  with files.open(file_name, 'a') as f:
    f.write(data)
  files.finalize(file_name)
  blob_key = files.blobstore.get_blob_key(file_name)
  return blob_key