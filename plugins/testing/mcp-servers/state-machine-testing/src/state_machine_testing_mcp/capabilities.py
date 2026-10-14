"""宿主能力探测结果分类；不启动进程或修改宿主配置。"""


def classify_probe(tool_names, *, disabled=False, validation_report=None,
                   parameter_error=False, transport_error=None):
    if disabled:
        return "disabled"
    if transport_error:
        return "connection_failed"
    if "validate_state_machine" not in tool_names:
        return "unavailable"
    if parameter_error:
        return "parameter_error"
    if validation_report is not None and validation_report.get("overall_status") not in {"pass", "warn", "fail"}:
        return "unexpected_response"
    return "available"
