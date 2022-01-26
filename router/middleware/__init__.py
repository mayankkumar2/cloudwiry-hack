import sqlalchemy.exc
from jose import JWTError
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from models.user import User
import connection.con
import utils.jwt
import re


async def bearer_token(access_token: None | str = None, authorization: str | None = Header(None)):
    if access_token is None and authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="access_token query parameter or authorization beared token is required"
        )
    try:
        if access_token is None:
            token = re.search('Bearer .{20,2048}', authorization, re.IGNORECASE)
            return token.string.split(" ")[-1]
        else:
            return access_token
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


async def get_credentials(token: str = Depends(bearer_token)):
    try:
        payload = await utils.jwt.jwt_decode(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return payload


async def get_user(data: dict = Depends(get_credentials), db: Session = Depends(connection.con.get_pg_db)):
    try:
        username = data.get("username")
        user = db.query(User).filter_by(username=username).one()
        return user
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
