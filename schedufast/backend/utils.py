import tempfile
def save_temp_file(file_bytes, suffix=".pdf"):
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
        temp.write(file_bytes)
        temp.flush()
        return temp.name