import logging


def setup_log(project_name='draft', level=logging.INFO):
  log_file = f'{project_name}.log'
  logger = logging.getLogger(project_name)
  formatter = logging.Formatter('[%(asctime)s] %(message)s', "%m/%d %H:%M:%S")
  file_handler = logging.FileHandler(log_file)
  file_handler.setFormatter(formatter)
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)

  if (logger.hasHandlers()):
    logger.handlers.clear()

  logger.setLevel(level)
  logger.addHandler(file_handler)
  logger.addHandler(stream_handler)
  return logger


def reset_log(project_name='draft'):
  with open(f'{project_name}.log', 'w'):
    pass


def read_log(project_name='draft'):
  with open(f'{project_name}.log', 'r') as f:
    return f.read()
