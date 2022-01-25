import sqlalchemy.exc
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status
from schemas.user_requests import CreateUserRequest, UserLoginRequest
from connection.con import get_pg_db
from models.user import User

router = APIRouter()


@router.post("/create")
def create_user(user: CreateUserRequest, db: Session = Depends(get_pg_db)):
    u = User(username=user.username)
    u.set_password(user.password)
    db.add(u)
    db.commit()
    return {'status': 'ok'}


@router.post("/login")
def login_user(usr: UserLoginRequest, db: Session = Depends(get_pg_db)):
    try:
        user = db.query(User).filter_by(username=usr.username).one()
        if not user.cmp_password(user.password, usr.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid password"
            )

        return user

    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )


@router.get('/')
def home():
    return 'Ok'
