import sys

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Отображает прогресс-бар в консоли"""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total: 
        sys.stdout.write('\n')