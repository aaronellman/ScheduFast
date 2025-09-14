import tempfile

def save_temp_file(file_bytes, suffix=".pdf"):
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
        temp.write(file_bytes)
        temp.flush()
        return temp.name
    
def callback(request_id, response, exception):
    if exception:
        print(f"Error in request {request_id}: {exception}")
    else:
        print(f"Request {request_id} succeeded: {response}")