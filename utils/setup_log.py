import logging

class TruncateFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if len(msg) > 1200:
            return msg[:1197] + "..."
        return msg

class ForceWerkzeugDebugFilter(logging.Filter):
    """Ép mọi log của werkzeug thành DEBUG để chỉ đi vào debug.log"""
    def filter(self, record):
        if record.name.startswith("werkzeug"):
            record.levelno = logging.DEBUG
            record.levelname = "DEBUG"
        return True

def setup_logging():
    # Xóa tất cả handler mặc định (vd: discord.py, flask thêm sẵn)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Formatter chung
    formatter = TruncateFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File log chính (INFO+)
    info_handler = logging.FileHandler("bot.log", encoding="utf-8")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # File debug (chỉ DEBUG)
    debug_handler = logging.FileHandler("debug.log", encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(lambda r: r.levelno == logging.DEBUG)  # chỉ DEBUG
    debug_handler.setFormatter(formatter)

    # Cấu hình logger gốc
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # để capture hết
    root_logger.addHandler(console_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(debug_handler)

    # Thêm filter ép werkzeug xuống DEBUG
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.addFilter(ForceWerkzeugDebugFilter())
    werkzeug_serving_logger = logging.getLogger("werkzeug.serving")
    werkzeug_serving_logger.addFilter(ForceWerkzeugDebugFilter())
