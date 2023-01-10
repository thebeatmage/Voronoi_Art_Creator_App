from flask import Flask, request, render_template, send_file
from PIL import Image, ImageFilter, ImageColor
import tempfile
import random
import math
import seaborn as sns
from matplotlib import pyplot as plt

app = Flask(__name__)

app.debug = False

def generate_voronoi_diagram(width, height, num_cells, mean_x, stdv_x, mean_y, stdv_y,
                             colorMap1, colorMap2, colorMap3, blend_multiplier):

    # Combine Color Maps:
    colorMapCom1 = [colorMap1, colorMap2, colorMap3]
    colorMapCom2 = [colorMap2, colorMap3, colorMap1]
    colorMapCom3 = [colorMap3, colorMap1, colorMap2]

    colorPallette1 = 'blend:' + ','.join(colorMapCom1)
    colorPallette2 = 'blend:' + ','.join(colorMapCom2)
    colorPallette3 = 'blend:' + ','.join(colorMapCom3)

    if blend_multiplier > 256:
        blend_number = 256
    else:
        blend_number = blend_multiplier

    # Create variable instances
    image = Image.new("RGB", (width, height))
    putpixel = image.putpixel
    imgx, imgy = image.size
    nx = []
    ny = []
    nr = []
    ng = []
    nb = []

    # Define color palettes (For Linked Color Palletes)
    colors1 = sns.color_palette(colorPallette1, blend_number)
    colors2 = sns.color_palette(colorPallette2, blend_number)
    colors3 = sns.color_palette(colorPallette3, blend_number)
    
    # Define sites and colors for each site
    for i in range(num_cells):
        nx.append(int(random.gauss(mean_x, stdv_x)))
        ny.append(int(random.gauss(mean_y, stdv_y)))
        
        if i%2 == 0:
            temp_color = colors1[random.randrange(0, blend_number)]
        elif i%3 == 0:
            temp_color = colors2[random.randrange(0, blend_number)]
        else:
            temp_color = colors3[random.randrange(0, blend_number)]
            
        nr.append(int(temp_color[0]*256))
        ng.append(int(temp_color[1]*256))
        nb.append(int(temp_color[2]*256))
    
    # Create diagram
    for y in range(imgy):
        for x in range(imgx):
            dmin = math.hypot(imgx-1, imgy-1)
            j = -1
            for i in range(num_cells):
                d = math.hypot(nx[i]-x, ny[i]-y)
                if d < dmin:
                    dmin = d
                    j = i
            putpixel((x, y), (nr[j], ng[j], nb[j]))
    # Smooth Edges:
    image = image.filter(ImageFilter.SMOOTH)
    return image

@app.route('/generate_diagram', methods=['GET', 'POST'])
def generate_diagram():
    if request.method == 'POST':
        # Get user-specified values from the form
        colorList1 = request.form['colorList1']
        colorList2 = request.form['colorList2']
        colorList3 = request.form['colorList3']
        width = int(request.form['width'])
        height = int(request.form['height'])
        num_cells = int(request.form['num_cells'])
        blend_multiplier = int(request.form['blend_multiplier'])
        mean_x = width // 2
        stdv_x = width // 2
        mean_y = height // 2
        stdv_y = height // 2
        
        # Generate the Voronoi diagram
        image = generate_voronoi_diagram(width=width, height=height, num_cells=num_cells,
                                         mean_x=mean_x, stdv_x=stdv_x, mean_y=mean_y, stdv_y=stdv_y,
                                         colorMap1=colorList1,colorMap2=colorList2, colorMap3=colorList3, 
                                         blend_multiplier=blend_multiplier)
        
        # Save the image to a temporary file 
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir='./PNG/') as f:
            image.save(f, 'PNG')
            f.seek(0)
            return send_file(f.name, mimetype='image/png')
    else:
        # Render the form template
        return render_template('form.html')

@app.route('/')
def home():
    return render_template('form.html')

if __name__ == '__main__':
    app.run()

