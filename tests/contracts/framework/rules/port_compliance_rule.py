import inspect
from typing import Any, get_origin, get_type_hints


# ==========================================================
# TYPE HELPERS
# ==========================================================
def _is_dict_like(t):
    return get_origin(t) is dict or t is dict


def _is_compatible_type(port_t, impl_t):
    if port_t == impl_t:
        return True

    # dict vs dict[str, Any]
    if _is_dict_like(port_t) and _is_dict_like(impl_t):
        return True

    return False


# ==========================================================
# MAIN VALIDATOR
# ==========================================================
def ensure_port_compliance(instance: Any, port: type, name: str | None = None):
    label = name or instance.__class__.__name__

    # ==========================================================
    # 1. interface compliance (Protocol-safe)
    # ==========================================================
    for attr in dir(port):
        if attr.startswith("_"):
            continue

        if callable(getattr(port, attr)):
            if not hasattr(instance, attr):
                raise AssertionError(f"[PORT VIOLATION] {label} missing method '{attr}'")

    # ==========================================================
    # 2. métodos
    # ==========================================================
    port_methods = [m for m in dir(port) if callable(getattr(port, m)) and not m.startswith("_")]

    for method_name in port_methods:
        port_method = getattr(port, method_name)

        impl_method = getattr(type(instance), method_name, None)
        if impl_method is None:
            continue

        port_sig = inspect.signature(port_method)
        impl_sig = inspect.signature(impl_method)

        # ------------------------------------------------------
        # async vs sync
        # ------------------------------------------------------
        if inspect.iscoroutinefunction(port_method):
            if not inspect.iscoroutinefunction(impl_method):
                raise AssertionError(f"[ASYNC MISMATCH] {label}.{method_name} must be async")
        else:
            if inspect.iscoroutinefunction(impl_method):
                raise AssertionError(
                    f"[ASYNC MISMATCH] {label}.{method_name} must be sync (async not allowed)"
                )

        # ------------------------------------------------------
        # parâmetros
        # ------------------------------------------------------
        _validate_parameters(label, method_name, port_sig, impl_sig)

        # ------------------------------------------------------
        # retorno
        # ------------------------------------------------------
        _validate_return_type(label, method_name, port_method, impl_method)


# ==========================================================
# PARAM VALIDATION (mais inteligente)
# ==========================================================
def _validate_parameters(label, method_name, port_sig, impl_sig):
    port_params = list(port_sig.parameters.values())[1:]  # remove self
    impl_params = list(impl_sig.parameters.values())[1:]

    for i, port_param in enumerate(port_params):
        if i >= len(impl_params):
            raise AssertionError(
                f"[SIGNATURE MISMATCH] {label}.{method_name} missing param '{port_param.name}'\n"
                f"Port: {port_sig}\nImpl: {impl_sig}"
            )

        impl_param = impl_params[i]

        # kind (positional / keyword-only)
        if impl_param.kind != port_param.kind:
            raise AssertionError(
                f"[PARAM KIND MISMATCH] {label}.{method_name} param '{port_param.name}'"
            )


# ==========================================================
# RETURN TYPE VALIDATION (flexível)
# ==========================================================
def _validate_return_type(label, method_name, port_method, impl_method):
    try:
        port_hints = get_type_hints(port_method)
        impl_hints = get_type_hints(impl_method)
    except Exception:
        return

    port_return = port_hints.get("return")
    impl_return = impl_hints.get("return")

    if port_return is None or impl_return is None:
        return

    if not _is_compatible_type(port_return, impl_return):
        raise AssertionError(
            f"[RETURN TYPE MISMATCH] {label}.{method_name}\n"
            f"Port: {port_return}\n"
            f"Impl: {impl_return}"
        )
