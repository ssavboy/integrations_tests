# in future can take value from .env file

LABEL = "labelfordb"
TIMEOUT = 60
BASE_URL = "http://example.com/api/"
CONTENT_URL = "http://example.cms.com/api/"
ENDPOINTS = {
    # CONTENT SERVER -->
    "general_categories": "generalcategories",
    # CONTENT SERVER <--
    "auth": "auth/",  # OK
    "users": "users",  # OK
    "contact_tickets": "contacttickets",  # OK
    "new_teacher": "newteacher",  # OK
    "fav-teachers": "favoriteteachers",  # OK
    "lessons": "lessons",
    "Teaching_Experiences": "TeachingExperiences",
    "teacher_documents": "TeacherDocuments",
    "learning_materials": "LearningMaterials",
}
# AUTH ----->
ENDPOINTS["signup"] = f"{ENDPOINTS['auth']}signup"  # OK
ENDPOINTS["set_password"] = f"{ENDPOINTS['auth']}set-password"  # OK
ENDPOINTS["forgot_password"] = f"{ENDPOINTS['auth']}forgot-password"  # OK
ENDPOINTS["reset_password"] = f"{ENDPOINTS['auth']}reset-password"  # OK
ENDPOINTS["login"] = f"{ENDPOINTS['auth']}login"  # OK
ENDPOINTS["change_password"] = f"{ENDPOINTS['auth']}change-password"  # OK
ENDPOINTS["users"] = "Users"
ENDPOINTS["get-profile"] = "Users/get-profile"
# <--- END AUTH

# USERS --->
ENDPOINTS["get-profile"] = f"{ENDPOINTS['users']}/get-profile"  # OK
ENDPOINTS["hobbies"] = f"{ENDPOINTS['users']}/hobbies"  # -------> NOT OK <-------
ENDPOINTS["interests"] = f"{ENDPOINTS['users']}/interests"  # -------> NOT OK <-------
ENDPOINTS["telegram"] = f"{ENDPOINTS['users']}/telegram"  # -------> ? <-------
ENDPOINTS["user-languages"] = "UserLanguages"  # -------> ? <-------

# <--- END USERS

# NEW-TEACHERS
ENDPOINTS["upload-id-document"] = (
    f"{ENDPOINTS['new_teacher']}/upload-id-document"  # -------> OK <-------
)
ENDPOINTS["upload-education-document"] = (
    f"{ENDPOINTS['new_teacher']}/upload-education-document"  # -------> OK <-------
)
ENDPOINTS["upload-additional-document"] = (
    f"{ENDPOINTS['new_teacher']}/upload-additional-document"  # -------> OK <-------
)
# END NEW-TEACHERS

# NEW TeacherEducations
ENDPOINTS["teacher_educations"] = "TeacherEducations"

# END TeacherEducations

# Accounting
ENDPOINTS.setdefault("accounting", "Accounting")
ENDPOINTS["accounting_deposit"] = f"{ENDPOINTS['accounting']}/deposit"
ENDPOINTS["accounting_buy_package"] = f"{ENDPOINTS['accounting']}/buy-package"
ENDPOINTS["accounting_user_account_transactions"] = f"{ENDPOINTS['accounting']}/user-account-transactions"
ENDPOINTS["accounting_user_account_transactions"] = f"{ENDPOINTS['accounting']}/user-account-transactions"
ENDPOINTS["accounting_user_account_balance"] = f"{ENDPOINTS['accounting']}/user-account-balance"
ENDPOINTS["accounting_terminate_package"] = f"{ENDPOINTS['accounting']}/terminate-package"

