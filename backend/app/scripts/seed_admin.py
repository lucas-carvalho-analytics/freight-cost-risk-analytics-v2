import argparse
from getpass import getpass

from sqlalchemy import select

from app.auth.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cria ou atualiza o usuario admin inicial.",
    )
    parser.add_argument("--email", required=True, help="Email do admin.")
    parser.add_argument(
        "--full-name",
        default="Admin",
        help="Nome completo do admin.",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="Senha do admin (modo nao-interativo). Se omitido, solicita via terminal.",
    )
    return parser.parse_args()


def prompt_password() -> str:
    password = getpass("Admin password: ")
    if not password:
        raise SystemExit("Admin password cannot be empty.")

    password_confirmation = getpass("Confirm admin password: ")
    if password != password_confirmation:
        raise SystemExit("Password confirmation does not match.")

    return password


def main() -> None:
    args = parse_args()
    email = args.email.strip().lower()
    password = args.password if args.password else prompt_password()

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))

        if user is None:
            user = User(
                email=email,
                full_name=args.full_name.strip(),
                password_hash=hash_password(password),
                is_active=True,
            )
            session.add(user)
            action = "created"
        else:
            user.full_name = args.full_name.strip()
            user.password_hash = hash_password(password)
            user.is_active = True
            action = "updated"

        session.commit()

    print(f"Admin user {action}: {email}")


if __name__ == "__main__":
    main()
