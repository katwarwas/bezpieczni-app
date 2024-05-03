from fastapi import HTTPException

def title_exception():
    return HTTPException(status_code=422, detail="Tytuł jest wymagany.")