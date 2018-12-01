UPE Coding Challenge Submission
----
Nihar Mitra, Fall 2018

To run this solution use python3, make sure the `requests` library is installed.
Then use Python 3 to execute maze.py. For example, `python3 maze.py`

This should execute the program.

## Other Documentation
These are notes that I found relevant to development.

### Importing Modules
The requests library had to be installed using pip. However, as a macOS user who uses Homebrew, I had multiple versions of Python 3 installed. This meant that `pip install requests` installed the module for the OSX default Python, while `python3 make.py` would execute the Homebrew Python and not find the module. Using `python3 -m pip install --upgrade requests` fixed this issue.

### Requests Library:
Different HTTP requests are made using different function names, e.g. `requests.post()` `requests.get()` etc.

To send data along with the requests:

* Headers can be sent using a dictionary and are passed in using the `headers` formal parameter, e.g. ```requests.post(headers={"content-type":
"application/x-www-form-url"}```
* Body information is sent using a JSON formatted dictionary passed into the `data` formal parameter, e.g. `requests.post(data=json.dumps({"user":"test"})`
* Query strings are sent as dictionaries, using the `params` formal parameter. E.g. `requests.post(params={'token': 'x'})`

The requests return an object with various attributes. Key attributes include:

* Status code: `r.status_code`, can be compared with certain preset codes, such as `requests.codes.ok`