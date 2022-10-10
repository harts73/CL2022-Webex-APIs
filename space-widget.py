from flask import Flask
import os

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SPACE_ID = os.getenv("SPACE_ID")


@app.route('/', methods=['GET', 'POST'])
def init():
    html = f"""
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://code.s4d.io/widget-space/production/main.css">
    
    <!-- Latest compiled and minified JavaScript -->
    <script src="https://code.s4d.io/widget-space/production/bundle.js"></script>
    
    <div id="my-space-widget" />
    
    <script>
      // Grab DOM element where widget will be attached
      var widgetEl = document.getElementById('my-space-widget');
    
      // Initialize a new Space widget
      webex.widget(widgetEl).spaceWidget({{
        accessToken: '{ACCESS_TOKEN}',
        destinationType: 'spaceId',
        destinationId: '{SPACE_ID}'
      }});
    </script> 
    """
    return html


if __name__ == '__main__':
    app.run(host='localhost', port=9090, debug=True)
