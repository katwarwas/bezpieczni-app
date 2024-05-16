from fastapi import HTTPException, status

def title_exception():
    return HTTPException(status_code=422, detail="Tytuł jest wymagany.")

def post_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )

def admin_exception():
     return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to delete"
    )
    