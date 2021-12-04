## Install

### Setup your virtual environment, Python 3.8.10+

 * python3 -m virtualvenv venv
 * cd venv
 * source bin/env
 * pip3 install -r requirements.txt

Start Spyder, open dash_app_test_1.py in Spyder, and run it.
It should start a DASH server.
Point your browser to ```localhost:8050```, the default DASH server settings, and you should see it.

### Stylesheets | CSS

DASH can use custom style sheets, and one can point external ones, i.e

```python
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
```

Or a relative location, as simple as that.
Uncomment that in the py file and specify the css location

```python
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
```

Or if one for example creates a custom CSS in css/ dir
```python
custom_css = os.path.join(os.getcwd(), "css", "custom_css_filename.css")
app = dash.Dash(__name__, external_stylesheet=custom_css)
```

Load ```lab_user_data.py``` on Spyder, run and point the browser to your ```127.0.0.1:8050```



 
