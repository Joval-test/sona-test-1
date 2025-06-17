import time
import functools
import inspect
import traceback
import logging


logging.basicConfig(
    # level=logging.INFO,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("admin_app")

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
            except Exception as e:
                error_msg = f"Error in {func.__qualname__}: {str(e)}"
                error_traceback = traceback.format_exc()
                logger.error(f"{error_msg}\n{error_traceback}")
                print(f"[ERROR] {error_msg}")
                raise
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
                
                log_message = (
                    f"[{STAGE_NAMES.get(stage, 'STAGE ?')}] "
                    f"Function: {func_name}\n"
                    f"  Input: {arg_dict}\n"
                    f"  Output: {result}\n"
                    f"  Time: {elapsed:.4f}s\n"
                    f"{'-'*40}"
                )
                
                print(log_message)
                logger.info(log_message)
        return wrapper
    return decorator
