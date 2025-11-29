# query_user.py
from models import Session, UserView

def get_user_view(user_id):
    s = Session()
    try:
        uv = s.query(UserView).filter_by(id=user_id).first()
        return None if uv is None else {"id": uv.id, "username": uv.username, "email": uv.email, "display_name": uv.display_name}
    finally:
        s.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python query_user.py <user_id>")
        sys.exit(1)
    uid = int(sys.argv[1])
    out = get_user_view(uid)
    if not out:
        print("User view not found (projection may not have run yet).")
    else:
        print(out)
