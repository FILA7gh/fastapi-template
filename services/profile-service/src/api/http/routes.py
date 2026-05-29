from fastapi import APIRouter
from src.api.http.profiles.admin import router as profile_admin_router
from src.api.http.profiles.user import router as profile_user_router
from src.api.http.seller_account.admin import router as seller_account_admin_router
from src.api.http.seller_account.user import router as seller_account_user_router
from src.api.http.stores.admin import router as admin_store_router
from src.api.http.stores.user import router as store_router

main_router = APIRouter(prefix="/api/profile")

main_router.include_router(profile_admin_router)
main_router.include_router(profile_user_router)

main_router.include_router(seller_account_admin_router)
main_router.include_router(seller_account_user_router)

main_router.include_router(store_router)
main_router.include_router(admin_store_router)
