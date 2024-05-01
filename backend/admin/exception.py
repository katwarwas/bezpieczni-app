from fastapi import HTTPException, status

def get_user_exist_exception():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Email already registered",
    )


def user_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


def get_invalid_token_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
