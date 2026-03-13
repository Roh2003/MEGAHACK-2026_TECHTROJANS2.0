"""
Central HTTP status codes — import from here instead of hardcoding numbers.

Usage:
    from shared.status_codes import HTTP

    raise HTTPException(status_code=HTTP.NOT_FOUND, detail="Job not found")
    return JSONResponse(status_code=HTTP.CREATED, content={...})
"""


class HTTP:
    # ── 2xx Success ──────────────────────────────────────────
    OK                    = 200  # GET, PUT — request succeeded
    CREATED               = 201  # POST — resource created
    ACCEPTED              = 202  # async operation accepted, not yet complete
    NO_CONTENT            = 204  # DELETE — success, nothing to return

    # ── 3xx Redirection ──────────────────────────────────────
    MOVED_PERMANENTLY     = 301
    FOUND                 = 302
    NOT_MODIFIED          = 304

    # ── 4xx Client Errors ────────────────────────────────────
    BAD_REQUEST           = 400  # malformed request / validation error
    UNAUTHORIZED          = 401  # not authenticated (no/invalid token)
    FORBIDDEN             = 403  # authenticated but not allowed
    NOT_FOUND             = 404  # resource does not exist
    METHOD_NOT_ALLOWED    = 405
    CONFLICT              = 409  # resource already exists (e.g. duplicate email)
    GONE                  = 410  # resource permanently deleted
    UNPROCESSABLE_ENTITY  = 422  # passed validation but semantically wrong
    TOO_MANY_REQUESTS     = 429  # rate limit exceeded

    # ── 5xx Server Errors ────────────────────────────────────
    INTERNAL_SERVER_ERROR = 500  # unexpected server failure
    NOT_IMPLEMENTED       = 501
    BAD_GATEWAY           = 502
    SERVICE_UNAVAILABLE   = 503  # server down / overloaded
    GATEWAY_TIMEOUT       = 504
