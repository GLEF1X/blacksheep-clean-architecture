from src.web.bootstrap import ApplicationBuilder


class InsecureApplicationBuilder(ApplicationBuilder):
    def _setup_security(self) -> None:
        pass
