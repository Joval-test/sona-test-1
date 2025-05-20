import time
import functools
import inspect

STAGE_NAMES = {
    1: "STAGE 1 (CRITICAL)",
    2: "STAGE 2 (IMPORTANT)",
    3: "STAGE 3 (USEFUL)",
    4: "STAGE 4 (OPTIONAL)"
}

def stage_log(stage=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = None
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start
                func_name = func.__qualname__
                try:
                    sig = inspect.signature(func)
                    bound = sig.bind_partial(*args, **kwargs)
                    bound.apply_defaults()
                    arg_dict = dict(bound.arguments)
                except Exception:
                    arg_dict = {"args": args, "kwargs": kwargs}
                print(
                    f"[{STAGE_NAMES.get(stage, 'STAGE ?')}] "
                    f"Function: {func_name}\n"
                    f"  Input: {arg_dict}\n"
                    f"  Output: {result}\n"
                    f"  Time: {elapsed:.4f}s\n"
                    f"{'-'*40}"
                )
        return wrapper
    return decorator