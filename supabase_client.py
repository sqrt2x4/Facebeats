from supabase import create_client


SUPABASE_URL = "https://ilmyjtjplwppmlsjtdec.supabase.co"
SUPABASE_KEY = "sb_publishable_k4FrVQFYFLIdROMQ0P7KtA_Nmuy5B6p"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)