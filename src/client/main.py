from client import Client
from ui.login_window import LoginWindow


def main():
    client = Client()
    LoginWindow(client).show()


if __name__ == "__main__":
    main()