from lib.assetwatch import assetwatch
from mysubtree.web.assetwatch import assets_dir, public_dir, http_path
 
assetwatch.run_once(assets_dir, public_dir, http_path)