from dishka import Provider, Scope, provide
from src.application.use_cases.profiles import (
    CreateProfileUseCase,
    DeleteAccountUseCase,
    DeleteProfileAvatarUseCase,
    GetProfileUseCase,
    ListProfileUseCase,
    UpdateProfileAvatarUseCase,
    UpdateProfileUseCase,
)
from src.application.use_cases.seller_accounts import (
    AdminSellerAccountDetailUseCase,
    AdminSellerAccountListUseCase,
    AdminSellerAccountSetStatusUseCase,
    AdminVerificationSetStatusUseCase,
    CreateSellerAccountUseCase,
    UpdateSellerAccountUseCase,
    VerifySellerAccountUseCase,
)
from src.application.use_cases.stores import (
    AdminListStoresUseCase,
    AdminStoreUseCase,
    CreateStoreUseCase,
    DeleteStoreUseCase,
    GetStoreUseCase,
    ListMyStoresUseCase,
    ListStoresUseCase,
    UpdateStoreImageUseCase,
    UpdateStoreUseCase,
)


class UseCaseProvider(Provider):
    # profiles
    create_profile_use_case = provide(CreateProfileUseCase, scope=Scope.REQUEST)
    get_profile_use_case = provide(GetProfileUseCase, scope=Scope.REQUEST)
    update_profile_use_case = provide(UpdateProfileUseCase, scope=Scope.REQUEST)
    update_profile_avatar_use_case = provide(
        UpdateProfileAvatarUseCase, scope=Scope.REQUEST
    )
    delete_profile_avatar_use_case = provide(
        DeleteProfileAvatarUseCase, scope=Scope.REQUEST
    )
    list_profiles_use_case = provide(ListProfileUseCase, scope=Scope.REQUEST)

    # seller accounts
    create_seller_account_use_case = provide(
        CreateSellerAccountUseCase, scope=Scope.REQUEST
    )
    update_seller_account_use_case = provide(
        UpdateSellerAccountUseCase, scope=Scope.REQUEST
    )
    verify_seller_account_uc = provide(VerifySellerAccountUseCase, scope=Scope.REQUEST)
    admin_seller_account_list_use_case = provide(
        AdminSellerAccountListUseCase, scope=Scope.REQUEST
    )
    admin_seller_account_detail_use_case = provide(
        AdminSellerAccountDetailUseCase, scope=Scope.REQUEST
    )
    admin_seller_account_set_status_use_case = provide(
        AdminSellerAccountSetStatusUseCase, scope=Scope.REQUEST
    )
    admin_seller_account_set_verification_status_uc = provide(
        AdminVerificationSetStatusUseCase, scope=Scope.REQUEST
    )

    delete_account_use_case = provide(DeleteAccountUseCase, scope=Scope.REQUEST)

    # stores
    get_store_use_case = provide(GetStoreUseCase, scope=Scope.REQUEST)
    create_store_use_case = provide(CreateStoreUseCase, scope=Scope.REQUEST)
    update_store_use_case = provide(UpdateStoreUseCase, scope=Scope.REQUEST)
    update_store_image_uc = provide(UpdateStoreImageUseCase, scope=Scope.REQUEST)
    get_my_stores_use_case = provide(ListMyStoresUseCase, scope=Scope.REQUEST)
    delete_store_use_case = provide(DeleteStoreUseCase, scope=Scope.REQUEST)
    list_stores_uc = provide(ListStoresUseCase, scope=Scope.REQUEST)
    admin_list_stores_uc = provide(AdminListStoresUseCase, scope=Scope.REQUEST)
    admin_store_detail_uc = provide(AdminStoreUseCase, scope=Scope.REQUEST)
