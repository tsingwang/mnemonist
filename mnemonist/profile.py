from pathlib import Path


class Profile:

    def __init__(self):
        workdir = Path.home().joinpath(".mnemonist")
        workdir.mkdir(exist_ok=True)
        self.filepath = workdir.joinpath("config")
        if not self.filepath.exists():
            self.filepath.touch()

    @property
    def current_user(self):
        return self.read('USER', 'default')

    @current_user.setter
    def current_user(self, user: str):
        self.update('USER', user)

    @property
    def db_path(self):
        return Path.home().joinpath(".mnemonist/{}.sqlite3".format(self.read('USER', 'default')))

    def read(self, keyword, default=""):
        with open(self.filepath) as f:
            for line in f:
                if keyword in line:
                    return line.replace(keyword + "=", "").replace("\n", "")
        return default

    def update(self, keyword, content=None):
        if content:
            content = keyword + "=" + content
            if not content.endswith("\n"):
                content += "\n"

        lines = []
        with open(self.filepath) as f:
            lines = f.readlines()
        with open(self.filepath, "w") as f:
            for line in lines:
                if keyword in line:
                    continue
                f.write(line)
            if content:
                f.write(content)


profile = Profile()
