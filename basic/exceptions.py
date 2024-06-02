from fastapi import HTTPException, status

def post_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )
