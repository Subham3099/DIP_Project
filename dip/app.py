from flask import Flask, request, render_template, redirect, url_for, send_file
import cv2
import numpy as np

app = Flask(__name__)

def remove_color(img, color_hash, threshold):

    # Get user input for the color hash code
    if not (color_hash[0] == '#' and len(color_hash) == 7):
        print('Invalid input. Please enter a valid six-character hexadecimal value starting with "#".')

    if(color_hash=='#000000'):
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([80, 255, 30])
    else:
        # Convert the color hash code to BGR values
        bgr_color = tuple(int(color_hash[i:i+2], 16) for i in (1, 3, 5))[::-1]
        bgr_color = np.uint8([[bgr_color]])


        # Convert BGR to HSV color space
        hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)

        # Define range of color in HSV color space
        hue = hsv_color[0][0][0]
        lower_color = np.array([max(0,hue - threshold), 50, 50])
        upper_color = np.array([min(179,hue + threshold), 255, 255])

    # Apply color range filter to the image
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Define a structuring element for dilation
    kernel = np.ones((4, 4), np.uint8)

    # Apply dilation to the mask image
    mask = cv2.dilate(mask, kernel, iterations=1)

    # Apply the mask to remove the color range from the image
    result = cv2.inpaint(img, mask,5, cv2.INPAINT_TELEA)

    return result

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('input.html')

@app.route('/process', methods=['GET','POST'])
def process():
    # Get form data
    file = request.files['file']
    color_hash = request.form['color_hash']
    threshold = int(request.form['threshold'])

    # Read image file
    img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)

    cv2.imwrite('static/input.jpg', img)

    print(color_hash,threshold)

    # Process the image
    result = remove_color(img, color_hash, threshold)

    # Save the processed image to a file
    cv2.imwrite('static/result.jpg', result)

    # Redirect to the output page
    return redirect(url_for('output'))

@app.route('/output')
def output():
    return render_template('output.html', filename='result.jpg')

if __name__ == '__main__':
    app.run(debug=True)
