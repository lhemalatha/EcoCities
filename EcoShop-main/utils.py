import base64
from PIL import Image
from io import BytesIO

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(file_stream):
    try:
        image = Image.open(file_stream)
        buffered = BytesIO()
        image.save(buffered, format=image.format)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        raise ValueError("Invalid image format") from e
