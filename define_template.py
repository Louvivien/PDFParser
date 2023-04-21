import fitz  
import matplotlib.pyplot as plt
import json
import tempfile
import sys



# Define a template on the PDF
def open_pdf_and_define_coordinates(pdf_file):
    print("Opening PDF viewer...")
    print("Click on two points to define a rectangular field (top-left corner and bottom-right corner).")

    coordinates = []
    field_names = []

    def on_click(event):
        nonlocal coordinates
        x, y = event.xdata, event.ydata
        print(f"Clicked at {x}, {y}")
        coordinates.append((x, y))
        if len(coordinates) % 2 == 0:
            print("Two points selected.")
            field_name = input("Enter field name: ")
            field_names.append(field_name)
            print("Press 'Enter' to finish or 'c' to continue adding fields.")
            action = input()
            if action.lower() == 'c':
                print("Click on two points to define the next rectangular field.")
            else:
                plt.close()

    doc = fitz.open(pdf_file)
    page = doc[0]
    zoom = 4
    mat = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=mat)
    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        pixmap.save(temp_file.name, "png")
        image = plt.imread(temp_file.name)

    fig, ax = plt.subplots()
    ax.imshow(image)
    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()

    if len(coordinates) % 2 != 0:
        print("Error: Odd number of clicks. Exiting.")
        sys.exit(1)

    fields = []
    for i in range(len(coordinates) // 2):
        x1, y1 = coordinates[2 * i]
        x2, y2 = coordinates[2 * i + 1]
        x = min(x1, x2) / zoom
        y = min(y1, y2) / zoom
        w = abs(x1 - x2) / zoom
        h = abs(y1 - y2) / zoom
        fields.append(
            {"name": field_names[i],
             "coordinates": {"x": x, "y": y, "w": w, "h": h}}
        )
    return {"fields": fields}


def save_template(template, template_file):
    with open(template_file, "w") as f:
        json.dump(template, f, indent=4)

