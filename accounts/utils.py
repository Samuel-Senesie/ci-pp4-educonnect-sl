from PIL import Image, ImageFile
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


ImageFile.LOAD_TRUNCATED_IMAGES = True

def validate_and_resize_image(image_file, max_size=5 * 1024 * 1024, max_dimensions=(1024, 521)):
    
    if not image_file:
        raise ValidationError("No image file provided.")

    # Check file size
    if image_file.size > max_size:
        raise ValidationError(f"Image size should not exceed {max_size / (1024 * 1024):.2f} MB.")
    
    # Open the image
    try:
        image = Image.open(image_file)
    except Exception as e:
        raise ValidationError("Invalid image file.") from e
    
    # Validate file format
    valid_formats = {"JPEG", "PNG", "GIF"}
    if image.format not in valid_formats:
        raise ValidationError(f"Unsupported file format. Allowed formats are: {', '.join(valid_formats)}.")
    
    # Convert to RGB if necessary
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB") # Convert to JPEG-compatible format if needed

    # Resize the image
    image.thumbnail(max_dimensions, Image.Resampling.LANCZOS)

    # Save resized image to a temporary buffer
    temp_image = BytesIO()
    image.save(temp_image, format="JPEG", quality=85)
    temp_image.seek(0)

    return ContentFile(temp_image.read(), name=image_file.name)