from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import UserRegister, UserLogin, Token
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database import db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Inscription d'un nouvel utilisateur"""
    
    # Vérifier si l'utilisateur existe déjà
    if db.user_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )
    
    # Créer l'utilisateur
    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        is_admin=user_data.is_admin
    )
    
    # Sauvegarder
    db.save_user(user.username, user.to_dict())
    
    # Créer le token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "is_admin": user.is_admin,
            "name": user.name,
            "level": user.level
        }
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Connexion d'un utilisateur"""
    
    # Récupérer l'utilisateur
    user_data = db.get_user(credentials.username)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )
    
    user = User.from_dict(user_data)
    
    # Vérifier le mot de passe
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )
    
    # Créer le token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "is_admin": user.is_admin,
            "name": user.name,
            "level": user.level
        }
    }