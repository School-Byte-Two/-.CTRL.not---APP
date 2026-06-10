import tkinter as tk
from smilefjes_bouncer.app import BouncerApp


def main() -> None:
    root = tk.Tk()
    root.title("smilefjes-bouncer 😊")
    root.resizable(False, False)
    app = BouncerApp(root)
    app.run()


if __name__ == "__main__":
    main()
