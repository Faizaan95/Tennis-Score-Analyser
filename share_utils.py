# share_utils.py
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from reportlab.pdfgen import canvas
from kivy.utils import platform

# Android-specific
if platform == "android":
    from androidstorage4kivy import SharedStorage
    from jnius import autoclass
    Intent = autoclass("android.content.Intent")
    Uri = autoclass("android.net.Uri")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
else:
    SharedStorage = None  # Prevents crashes on non-Android devices

def generate_stats_image(stats_text):
    img_path = "stats.png"
    Window.screenshot(name=img_path)
    print(f"Stats saved as {img_path}")
    return img_path

def generate_stats_pdf(stats_text):
    pdf_path = "stats.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, stats_text)
    c.save()
    print(f"Stats saved as {pdf_path}")
    return pdf_path

def share_file(file_path, mime_type="application/pdf"):
    if platform == "android" and SharedStorage:
        file_uri = SharedStorage().copy_to_shared(file_path, mime_type)
        intent = Intent(Intent.ACTION_SEND)
        intent.setType(mime_type)
        intent.putExtra(Intent.EXTRA_STREAM, Uri.parse(file_uri))
        chooser = Intent.createChooser(intent, "Share via")
        PythonActivity.mActivity.startActivity(chooser)
    else:
        print(f"Sharing not supported on this platform. File saved at {file_path}")
