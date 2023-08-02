from gotrue.types import UserResponse
from supabase import Client, create_client


from app.constants import SUPABASE_URL, SUPABASE_KEY


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user(token: str):
    response: UserResponse = supabase.auth.get_user(token)

    return response
