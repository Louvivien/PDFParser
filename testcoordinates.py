import pdfplumber
from pynput import mouse

def on_click(x, y, button, pressed):
    if button == mouse.Button.left and pressed:
        if page_left <= x <= page_right and page_top <= y <= page_bottom:
            print(f"Clicked at ({x}, {y})")
            clicks.append((x, y))

# Open the PDF file
with pdfplumber.open("sample1.pdf") as pdf:
    # Get the first page
    page = pdf.pages[0]
    # Get the page width and height
    page_width, page_height = page.width, page.height

    # Calculate the bounds of the PDF on the screen
    display_scale_factor = 1.33  # You can adjust this value
    page_left = page.crop((0, 0, 1, 1)).bbox[0] * display_scale_factor
    page_bottom = (page_height - page.crop((0, 0, 1, 1)).bbox[3]) * display_scale_factor
    page_right = page_left + page_width * display_scale_factor
    page_top = page_bottom - page_height * display_scale_factor

    # Start listening for clicks
    clicks = []
    listener = mouse.Listener(on_click=on_click)
    listener.start()

    # Loop until the user clicks twice
    while len(clicks) < 2:
        if not listener.is_alive():
            break

    # Stop listening for clicks
    listener.stop()

# Convert the clicked coordinates to PDF coordinates
x1, y1 = clicks[0]
x2, y2 = clicks[1]
pdf_x1 = x1 * 72 / 96
pdf_y1 = (page_height - y1) * 72 / 96
pdf_x2 = x2 * 72 / 96
pdf_y2 = (page_height - y2) * 72 / 96

# Calculate the width and height of the field
width = abs(pdf_x2 - pdf_x1)
height = abs(pdf_y2 - pdf_y1)

print(f"PDF coordinates: ({pdf_x1}, {pdf_y1}, {width}, {height})")
